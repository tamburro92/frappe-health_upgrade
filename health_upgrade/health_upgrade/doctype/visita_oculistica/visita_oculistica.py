# Copyright (c) 2024, Tamburro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, nowtime

class ProceduraOculistica(Document):
	pass

@frappe.whitelist()
def make_procedura_oculistica(source_name, target_doc=None):
	stc = frappe.get_doc("Visita oculistica", source_name)
	tgt = frappe.new_doc("Visita oculistica")

	doclist = get_mapped_doc(
		"Visita oculistica",
		source_name,
		{
			"Visita oculistica": {
				"doctype": "Visita oculistica",
			}
		},
		target_doc
	)
	doclist.encounter_date = getdate()
	doclist.encounter_time = nowtime()
	doclist.appointment = ''

	return doclist


@frappe.whitelist()
def make_procedura_from_appointment(source_name, target_doc=None):
	doclist = get_mapped_doc(
		"Patient Appointment",
		source_name,
				{
			"Patient Appointment": {
				"doctype": "Visita oculistica",
				"field_map": [
					["appointment", "name"],
					["patient", "patient"],
					["practitioner", "practitioner"],
					["start_date", "appointment_date"],
					["start_time", "appointment_time"],
					["notes", "notes"],
					["company", "company"],
					["invoiced", "invoiced"],
				],
			}
		},
		target_doc
	)
	return doclist
