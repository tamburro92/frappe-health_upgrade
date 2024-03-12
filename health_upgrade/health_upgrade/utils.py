'''
Just ovverride method get_appointments_to_invoice and get_appointment_type_billing_details
because it doesn't return a liked to the real item, but just procedure name...
TODO: ASK a fix to healthcare github
'''

import json

import frappe
from frappe import _


from healthcare.healthcare.doctype.healthcare_settings.healthcare_settings import (
	get_income_account,
)
from healthcare.healthcare import utils
from healthcare.healthcare.utils import get_practitioner_billing_details


@frappe.whitelist()
def get_healthcare_services_to_invoice(patient, company):
	patient = frappe.get_doc("Patient", patient)
	items_to_invoice = []
	if patient:
		utils.validate_customer_created(patient)
		# Customer validated, build a list of billable services
		items_to_invoice += get_appointments_to_invoice(patient, company)
		items_to_invoice += utils.get_encounters_to_invoice(patient, company)
		items_to_invoice += utils.get_lab_tests_to_invoice(patient, company)
		items_to_invoice += utils.get_clinical_procedures_to_invoice(patient, company)
		items_to_invoice += utils.get_inpatient_services_to_invoice(patient, company)
		items_to_invoice += utils.get_therapy_plans_to_invoice(patient, company)
		items_to_invoice += utils.get_therapy_sessions_to_invoice(patient, company)

		return items_to_invoice
	

def get_appointments_to_invoice(patient, company):
	appointments_to_invoice = []
	patient_appointments = frappe.get_list(
		"Patient Appointment",
		fields="*",
		filters={
			"patient": patient.name,
			"company": company,
			"invoiced": 0,
			"status": ["not in", "Cancelled"],
		},
		order_by="appointment_date",
	)

	for appointment in patient_appointments:
		# Procedure Appointments
		if appointment.procedure_template:
			if frappe.db.get_value(
				"Clinical Procedure Template", appointment.procedure_template, "is_billable"
			):
				appointments_to_invoice.append(
					{
						"reference_type": "Patient Appointment",
						"reference_name": appointment.name,
						"service": frappe.db.get_value("Clinical Procedure Template", appointment.procedure_template, "item"),
					}
				)
		# Consultation Appointments, should check fee validity
		else:
			if frappe.db.get_single_value(
				"Healthcare Settings", "enable_free_follow_ups"
			) and frappe.db.exists("Fee Validity Reference", {"appointment": appointment.name}):
				continue  # Skip invoicing, fee validty present
			practitioner_charge = 0
			income_account = None
			service_item = None
			if appointment.practitioner:
				details = get_appointment_billing_item_and_rate(appointment)
				service_item = details.get("service_item")
				practitioner_charge = details.get("practitioner_charge")
				income_account = get_income_account(appointment.practitioner, appointment.company)
			appointments_to_invoice.append(
				{
					"reference_type": "Patient Appointment",
					"reference_name": appointment.name,
					"service": service_item,
					"rate": practitioner_charge,
					"income_account": income_account,
				}
			)

	return appointments_to_invoice

# get_appointment_billing_item_and_rate
# add logic procedure_template
@frappe.whitelist()
def get_appointment_billing_item_and_rate(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe.get_doc(doc)

	service_item = None
	practitioner_charge = None
	department = doc.medical_department if doc.doctype == "Patient Encounter" else doc.department
	service_unit = doc.service_unit if doc.doctype == "Patient Appointment" else None

	is_inpatient = doc.inpatient_record

	if doc.get("practitioner"):
		service_item, practitioner_charge = get_practitioner_billing_details(
			doc.practitioner, is_inpatient
		)

	if not service_item and doc.get("procedure_template"):
		service_item, appointment_charge = get_procedure_template_billing_details(doc.procedure_template)
		if not practitioner_charge:
			practitioner_charge = appointment_charge

	if not service_item and doc.get("appointment_type"):
		service_item, appointment_charge = get_appointment_type_billing_details(
			doc.appointment_type, department if department else service_unit, is_inpatient
		)
		if not practitioner_charge:
			practitioner_charge = appointment_charge

	if not service_item:
		service_item = get_healthcare_service_item(is_inpatient)

	if not service_item:
		throw_config_service_item(is_inpatient)

	if not practitioner_charge and doc.get("practitioner"):
		throw_config_practitioner_charge(is_inpatient, doc.practitioner)

	if not practitioner_charge and not doc.get("practitioner"):
		throw_config_appointment_type_charge(is_inpatient, doc.appointment_type)

	return {"service_item": service_item, "practitioner_charge": practitioner_charge}

def get_appointment_type_billing_details(appointment_type, dep_su, is_inpatient):
	from healthcare.healthcare.doctype.appointment_type.appointment_type import get_billing_details

	# if not dep_su:
	# 	return None, None

	item_list = get_billing_details(appointment_type, dep_su)
	service_item = None
	practitioner_charge = None

	if item_list:
		if is_inpatient:
			service_item = item_list.get("inpatient_visit_charge_item")
			practitioner_charge = item_list.get("inpatient_visit_charge")
		else:
			service_item = item_list.get("op_consulting_charge_item")
			practitioner_charge = item_list.get("op_consulting_charge")

	return service_item, practitioner_charge



def get_procedure_template_billing_details(procedure):
	item_list = None
	item_list = frappe.db.get_value(
			"Clinical Procedure Template",
			filters={"name": procedure},
			fieldname=[
				"item",
				"item_code",
				"rate"
			],
			as_dict=1,
		)
	service_item = None
	practitioner_charge = None

	if item_list:
		service_item = item_list.get("item")
		practitioner_charge = item_list.get("rate")

	return service_item, practitioner_charge
