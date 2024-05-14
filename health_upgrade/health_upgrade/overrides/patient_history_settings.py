
'''
Just of clone of  patient_history_settings with a path on validate_medical_record_required
'''
import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr

from healthcare.healthcare.page.patient_history.patient_history import get_patient_history_doctypes


def create_medical_record(doc, method=None):
	medical_record_required = validate_medical_record_required(doc)
	if not medical_record_required:
		return

	if frappe.db.exists("Patient Medical Record", {"reference_name": doc.name}):
		return

	subject = set_subject_field(doc)
	date_field = get_date_field(doc.doctype)
	medical_record = frappe.new_doc("Patient Medical Record")
	medical_record.patient = doc.patient
	medical_record.subject = subject
	medical_record.status = "Open"
	medical_record.communication_date = doc.get(date_field)
	medical_record.reference_doctype = doc.doctype
	medical_record.reference_name = doc.name
	medical_record.reference_owner = doc.owner
	medical_record.save(ignore_permissions=True)


def update_medical_record(doc, method=None):
	medical_record_required = validate_medical_record_required(doc)
	if not medical_record_required:
		return

	medical_record_id = frappe.db.exists("Patient Medical Record", {"reference_name": doc.name})

	if medical_record_id:
		subject = set_subject_field(doc)
		frappe.db.set_value("Patient Medical Record", medical_record_id, "subject", subject)

	else:
		create_medical_record(doc)


def delete_medical_record(doc, method=None):
	medical_record_required = validate_medical_record_required(doc)
	if not medical_record_required:
		return

	record = frappe.db.exists("Patient Medical Record", {"reference_name": doc.name})
	if record:
		frappe.delete_doc("Patient Medical Record", record, force=1)


def set_subject_field(doc):
	from frappe.utils.formatters import format_value

	meta = frappe.get_meta(doc.doctype)
	subject = ""
	patient_history_fields = get_patient_history_fields(doc)

	for entry in patient_history_fields:
		fieldname = entry.get("fieldname")
		if entry.get("fieldtype") == "Table" and doc.get(fieldname):
			formatted_value = get_formatted_value_for_table_field(
				doc.get(fieldname), meta.get_field(fieldname)
			)
			subject += frappe.bold(_(entry.get("label")) + ":") + "<br>" + cstr(formatted_value) + "<br>"

		else:
			if doc.get(fieldname):
				formatted_value = format_value(doc.get(fieldname), meta.get_field(fieldname), doc)
				subject += frappe.bold(_(entry.get("label")) + ":") + cstr(formatted_value) + "<br>"

	return subject


def get_date_field(doctype):
	dt = get_patient_history_config_dt(doctype)

	return frappe.db.get_value(dt, {"document_type": doctype}, "date_fieldname")


def get_patient_history_fields(doc):
	dt = get_patient_history_config_dt(doc.doctype)
	patient_history_fields = frappe.db.get_value(
		dt, {"document_type": doc.doctype}, "selected_fields"
	)

	if patient_history_fields:
		return json.loads(patient_history_fields)


def get_formatted_value_for_table_field(items, df):
	child_meta = frappe.get_meta(df.options)

	table_head = ""
	table_row = ""
	html = ""
	create_head = True
	for item in items:
		table_row += "<tr>"
		for cdf in child_meta.fields:
			if cdf.in_list_view:
				if create_head:
					table_head += "<td>" + cdf.label + "</td>"
				if item.get(cdf.fieldname):
					table_row += "<td>" + str(item.get(cdf.fieldname)) + "</td>"
				else:
					table_row += "<td></td>"
		create_head = False
		table_row += "</tr>"

	html += (
		"<table class='table table-condensed table-bordered'>" + table_head + table_row + "</table>"
	)

	return html


def get_patient_history_config_dt(doctype):
	if frappe.db.get_value("DocType", doctype, "custom"):
		return "Patient History Custom Document Type"
	else:
		return "Patient History Standard Document Type"


def validate_medical_record_required(doc):
	if (
		frappe.flags.in_patch
		or frappe.flags.in_install
		or frappe.flags.in_setup_wizard
	):
		return False

	if doc.doctype not in get_patient_history_doctypes():
		return False

	return True


def get_module(doc):
	module = doc.meta.module
	if not module:
		module = frappe.db.get_value("DocType", doc.doctype, "module")

	return module
