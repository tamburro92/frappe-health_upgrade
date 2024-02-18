'''
Just ovverride method get_appointments_to_invoice
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
				details = utils.get_appointment_billing_item_and_rate(appointment)
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
