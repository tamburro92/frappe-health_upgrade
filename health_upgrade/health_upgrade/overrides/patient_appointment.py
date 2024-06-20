# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt


import datetime
import json

import frappe
from erpnext.setup.doctype.employee.employee import is_holiday
from frappe import _
from health_upgrade.health_upgrade.doctype.whatsapp_settings.whatsapp_settings import send_whatsapp_sms
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, format_date, get_link_to_form, get_time, getdate
from healthcare.healthcare.doctype.patient_appointment.patient_appointment import PatientAppointment, get_income_account, check_employee_wise_availability, check_fee_validity, get_fee_validity, get_appointment_item, get_receivable_account
from erpnext.controllers.selling_controller import get_taxes_and_charges
from frappe.contacts.address_and_contact import (load_address_and_contact)
from healthcare.healthcare.utils import throw_config_appointment_type_charge, throw_config_practitioner_charge, throw_config_service_item, get_healthcare_service_item, get_practitioner_billing_details
from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
from health_upgrade.health_upgrade.utils import get_appointment_billing_item_and_rate

class PatientAppointmentHC(PatientAppointment):
	def validate(self):
		self.validate_overlaps()
		self.validate_based_on_appointments_for()
		self.validate_service_unit()
		self.set_appointment_datetime()
		self.validate_customer_created()
		self.set_status()
		self.set_title()
		self.update_event()
		self.set_postition_in_queue()

	def set_status(self):
		# skip if status is already Closed
		if self.status != "Closed":
			super().set_status()

@frappe.whitelist()
def get_earliest_available_physician_and_date(hc_procedure):
	pass


@frappe.whitelist()
def get_availability_dates(date, practitioner):
	date = getdate()

	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)

	map_date_slots, map_date_appoints = get_slots_and_appointments(date, practitioner)
	av_data = []
	for k,v in sorted(map_date_slots.items()):
		n_booked = map_date_appoints[k] if k in map_date_appoints else 0
		av_data.append({
			"original" : k.strftime("%Y-%m-%d"),
			"formatted" : "{} {} ({})".format(k.strftime("%A"), k.strftime("%d/%m/%Y") , (map_date_slots[k] - n_booked))
		})
	return {
		"physician": practitioner_doc.practitioner_name,
		"availability_data": av_data
	}
@frappe.whitelist()
def get_earliest_available_date(practitioner):
	date = getdate()
	map_date_slots, map_date_appoints = get_slots_and_appointments(date, practitioner)
	for k,v in sorted(map_date_slots.items()):
		n_booked = map_date_appoints[k] if k in map_date_appoints else 0
		if map_date_slots[k] - n_booked > 0:
			return k.strftime("%Y-%m-%d")
	
	frappe.throw(
		_("Healthcare Practitioner not available"), title=_("Not Available")
	)
	
def get_slots_and_appointments(date, practitioner):
	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)

	map_date_slots = {}
	map_date_appoints = {}
	practitioner = practitioner_doc.name
	for schedule_entry in practitioner_doc.practitioner_schedules:
		practitioner_schedule = frappe.get_doc("Practitioner Schedule", schedule_entry.schedule)

		if practitioner_schedule:
			for time_slot in practitioner_schedule.time_slots:
				if date > time_slot.hc_slot_date:
					continue
				if time_slot.hc_slot_date not in map_date_slots:
					map_date_slots[time_slot.hc_slot_date]=1
				else:
					map_date_slots[time_slot.hc_slot_date]+=1			

	filters = {
			"practitioner": practitioner,
			"appointment_date": ["in", map_date_slots.keys()],
			"status": ["not in", ["Cancelled"]],}

	appointments = frappe.get_all("Patient Appointment",filters=filters,
					fields=["name", "appointment_time", "duration", "status", "appointment_date"],)
	
	for appointment in appointments:
		if appointment.appointment_date not in map_date_appoints:
			map_date_appoints[appointment.appointment_date]=1
		else:
			map_date_appoints[appointment.appointment_date]+=1
	return (map_date_slots, map_date_appoints)
	

@frappe.whitelist()
def get_availability_data(date, practitioner, appointment):
	"""
	Get availability data of 'practitioner' on 'date'
	:param date: Date to check in schedule
	:param practitioner: Name of the practitioner
	:return: dict containing a list of available slots, list of appointments and time of appointments
	"""

	date = getdate(date)

	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)

	check_employee_wise_availability(date, practitioner_doc)

	if practitioner_doc.practitioner_schedules:
		slot_details = get_available_slots(practitioner_doc, date)
	else:
		frappe.throw(
			_(
				"{0} does not have a Healthcare Practitioner Schedule. Add it in Healthcare Practitioner master"
			).format(practitioner),
			title=_("Practitioner Schedule Not Found"),
		)

	if not slot_details:
		# TODO: return available slots in nearby dates
		frappe.throw(
			_("Healthcare Practitioner not available on {0}").format(date), title=_("Not Available")
		)

	if isinstance(appointment, str):
		appointment = json.loads(appointment)
		appointment = frappe.get_doc(appointment)

	fee_validity = "Disabled"
	if frappe.db.get_single_value("Healthcare Settings", "enable_free_follow_ups"):
		fee_validity = check_fee_validity(appointment, date, practitioner)
		if not fee_validity and not appointment.get("__islocal"):
			fee_validity = get_fee_validity(appointment.get("name"), date) or None

	if appointment.invoiced:
		fee_validity = "Disabled"

	return {"slot_details": slot_details, "fee_validity": fee_validity}

def get_available_slots(practitioner_doc, date):
	available_slots = slot_details = []
	practitioner = practitioner_doc.name

	for schedule_entry in practitioner_doc.practitioner_schedules:
		practitioner_schedule = frappe.get_doc("Practitioner Schedule", schedule_entry.schedule)

		if practitioner_schedule and not practitioner_schedule.disabled:
			available_slots = []
			for time_slot in practitioner_schedule.time_slots:
				if date == time_slot.hc_slot_date:
					available_slots.append(time_slot)

			if available_slots:
				appointments = []
				allow_overlap = 0
				service_unit_capacity = 0
				# fetch all appointments to practitioner by service unit
				filters = {
					"practitioner": practitioner,
					"service_unit": schedule_entry.service_unit,
					"appointment_date": date,
					"status": ["not in", ["Cancelled"]],
				}

				if schedule_entry.service_unit:
					slot_name = f"{schedule_entry.schedule}"
					allow_overlap, service_unit_capacity = frappe.get_value(
						"Healthcare Service Unit",
						schedule_entry.service_unit,
						["overlap_appointments", "service_unit_capacity"],
					)
					if not allow_overlap:
						# fetch all appointments to service unit
						filters.pop("practitioner")
				else:
					slot_name = schedule_entry.schedule
					# fetch all appointments to practitioner without service unit
					filters["practitioner"] = practitioner
					filters.pop("service_unit")

				appointments = frappe.get_all(
					"Patient Appointment",
					filters=filters,
					fields=["name", "appointment_time", "duration", "status", "appointment_date"],
				)

				slot_details.append(
					{
						"slot_name": slot_name,
						"service_unit": schedule_entry.service_unit,
						"avail_slot": available_slots,
						"appointments": appointments,
						"allow_overlap": allow_overlap,
						"service_unit_capacity": service_unit_capacity,
						"tele_conf": practitioner_schedule.allow_video_conferencing,
					}
				)
	return slot_details

@frappe.whitelist()
def unlink_and_delete_sales_invoice(appointment_id):

	appointment_doc = frappe.get_doc("Patient Appointment", appointment_id)
	ref_invoice = appointment_doc.ref_sales_invoice
	frappe.db.set_value(
	"Patient Appointment",
	appointment_doc.name,
	{
		"invoiced": 0,
		"ref_sales_invoice": None,
		"paid_amount": 0,
	})

	frappe.delete_doc_if_exists("Sales Invoice",ref_invoice)
	return ({"message":"ok"})


@frappe.whitelist()
def create_invoice(company, practitioner, patient, appointment_id, appointment_date):
	appointment_doc = frappe.get_doc("Patient Appointment", appointment_id)

	create_sales_invoice(appointment_doc)

def create_sales_invoice(appointment_doc, discount_percentage=0, discount_amount=0):
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.patient = appointment_doc.patient
	sales_invoice.customer = frappe.get_value("Patient", appointment_doc.patient, "customer")
	sales_invoice.due_date = getdate()
	sales_invoice.company = appointment_doc.company
	sales_invoice.debit_to = get_receivable_account(appointment_doc.company)
	sales_invoice.hc_practitioner = appointment_doc.practitioner
	sales_invoice.hc_appointment = appointment_doc.name

	# Set Items
	item = sales_invoice.append("items", {})
	item = get_appointment_item(appointment_doc, item)
	#item_price = frappe.get_doc("Item Price", {"item_code": appointment_doc.hc_procedure})
	paid_amount = flt(appointment_doc.paid_amount)

	# Set taxes
	#tax_bollo = frappe.get_value("Company", appointment_doc.company, "hc_default_bollo_template")
	# tax_zero_vat = frappe.get_value("Company", appointment_doc.company, "hc_default_zero_vat_template")
	mode_payment = frappe.get_value("Company", appointment_doc.company, "hc_default_mode_of_payment")
	sales_invoice.hc_mode_of_payment = mode_payment
	sales_invoice.naming_series = frappe.get_value("Company", appointment_doc.company, "hc_naming_series")
	
	#taxesBollo = get_taxes_and_charges("Sales Taxes and Charges Template", tax_bollo)
	taxDefault = get_default_taxes_and_charges("Sales Taxes and Charges Template", company= appointment_doc.company)

	for tax in taxDefault['taxes']:
		sales_invoice.append("taxes", tax)

	# Set payment mode
	sales_invoice.is_pos = 0
	
	payment = sales_invoice.append("payments", {})
	payment.mode_of_payment = mode_payment
	payment.amount = paid_amount
	'''
	sales_invoice.append("payment_schedule", dict(
		due_date= getdate().strftime("%Y-%m-%d"),
		invoice_portion=0,
		payment_amount=paid_amount,
		outstanding = paid_amount,
		mode_of_payment = mode_payment,
		base_payment_amount = 0,
	))
	'''
	#sales_invoice.set_payment_schedule()
	sales_invoice.set_missing_values(for_validate=True)
	sales_invoice.flags.ignore_mandatory = True

	sales_invoice.save(ignore_permissions=True)
	#sales_invoice.submit()
	frappe.msgprint(_("Sales Invoice {0} created").format(sales_invoice.name), alert=True)
	frappe.db.set_value(
		"Patient Appointment",
		appointment_doc.name,
		{
			"invoiced": 0,
			"ref_sales_invoice": sales_invoice.name,
			"paid_amount": paid_amount,
			"status": "Closed"
		},
	)
	appointment_doc.notify_update()


def get_appointment_item(appointment_doc, item):
	details = get_appointment_billing_item_and_rate(appointment_doc)
	charge = appointment_doc.paid_amount or details.get("practitioner_charge")
	item.item_code = details.get("service_item")
	item.description = _("Consulting Charges: {0}").format(appointment_doc.practitioner)
	item.income_account = get_income_account(appointment_doc.practitioner, appointment_doc.company)
	item.cost_center = frappe.get_cached_value("Company", appointment_doc.company, "cost_center")
	item.rate = charge
	item.amount = charge
	item.qty = 1
	item.reference_dt = "Patient Appointment"
	item.reference_dn = appointment_doc.name
	return item


@frappe.whitelist()
def check_patient_details(patient):
	patient_doc = frappe.get_doc("Patient", patient)
	customer_doc = frappe.get_doc("Customer",patient_doc.customer)
	load_address_and_contact(customer_doc)

	MANDATORY_FIELD_CUSTOMER = ['customer_name', 'fiscal_code']
	MANDATORY_FIELD_ADDRESS =	['address_line1','city','country','pincode','country_code']

	mandatory_missing_fields = []
	#check mandatory field:
	for field in MANDATORY_FIELD_CUSTOMER:
		if not getattr(customer_doc, field):
			mandatory_missing_fields.append(field)

	if not customer_doc.__onload.addr_list:
			mandatory_missing_fields += MANDATORY_FIELD_ADDRESS

	for addr in customer_doc.__onload.addr_list:
		for field in MANDATORY_FIELD_ADDRESS:
			if not getattr(addr, field):
				mandatory_missing_fields.append(field)
		break

	return {'missing_details' : mandatory_missing_fields,
		 	'patient_customer': customer_doc.name}


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions

	conditions = get_event_conditions("Patient Appointment", filters)

	data = frappe.db.sql(
		"""
		select
		`tabPatient Appointment`.name, `tabPatient Appointment`.patient, `tabPatient Appointment`.patient_name,
		`tabPatient Appointment`.practitioner, `tabPatient Appointment`.status, `tabPatient Appointment`.practitioner_name,
		`tabPatient Appointment`.duration,
		timestamp(`tabPatient Appointment`.appointment_date, `tabPatient Appointment`.appointment_time) as 'start',
		`tabAppointment Type`.color
		from
		`tabPatient Appointment`
		left join `tabAppointment Type` on `tabPatient Appointment`.appointment_type=`tabAppointment Type`.name
		where
		(`tabPatient Appointment`.appointment_date between %(start)s and %(end)s)
		and `tabPatient Appointment`.status != 'Cancelled' and `tabPatient Appointment`.docstatus < 2 {conditions}""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)

	for item in data:
		item.end = item.start + datetime.timedelta(minutes=item.duration)
		item.title = item.patient_name + ' ' + create_iniziali(item.practitioner_name)

	return data

def create_iniziali(input, skip_first=False):
	if not input:
		return ""
	pop_elm = ""
	input_arr = input.split()
	if skip_first and len(input_arr) >= 2:
		pop_elm = input_arr.pop(1)

	return pop_elm + ''.join([parola[0].upper() + '.' for parola in input_arr])



def send_appointment_reminder_whatsapp():
	if frappe.db.get_single_value("HC Settings", "send_appointment_reminder"):
		remind_before = frappe.db.get_single_value("HC Settings", "remind_before")
		reminder_dt = datetime.datetime.now() + datetime.timedelta(seconds = int(remind_before))

		appointment_list = frappe.db.get_all(
			"Patient Appointment",
			{
				"appointment_datetime": ["between", (datetime.datetime.now(), reminder_dt)],
				"reminded": 0,
				"status": ["!=", "Cancelled"],
			},
		)

		for appointment in appointment_list:
			doc = frappe.get_doc("Patient Appointment", appointment.name)
			message = frappe.db.get_single_value("HC Settings", "appointment_reminder_msg_wa")
			send_message(doc, message)
			frappe.db.set_value("Patient Appointment", doc.name, "reminded", 1)

def send_message(doc, message):
	patient_mobile = frappe.db.get_value("Patient", doc.patient, "mobile")
	if patient_mobile:
		context = {"doc": doc, "alert": doc, "comments": None}
		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		# jinja to string convertion happens here
		message = frappe.render_template(message, context)
		number = [patient_mobile]
		try:
			send_whatsapp_sms(number, message)
		except Exception as e:
			frappe.msgprint(_("WhatsApp SMS not sent, please check WhatsApp SMS Settings"), alert=True)