# Copyright (c) 2024, Tamburro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, nowtime
from frappe import _

class Prescrizionelenti(Document):
	def validate(self):
		self.set_title()

	def set_title(self):
		self.title = _("{0} with {1}").format(
			self.patient_name or self.patient, self.practitioner_name or self.practitioner
		)[:100]


@frappe.whitelist()
def make_prescrizioni_lenti(source_name, target_doc=None):

	doclist = get_mapped_doc(
		"Prescrizioni Lenti",
		source_name,
		{
			"Prescrizioni Lenti": {
				"doctype": "Prescrizioni Lenti",
			}
		},
		target_doc
	)
	doclist.encounter_date = getdate()
	doclist.encounter_time = nowtime()
	doclist.appointment = ''

	return doclist


@frappe.whitelist()
def make_prescrizione_from_appointment(source_name, target_doc=None):
	doclist = get_mapped_doc(
		"Patient Appointment",
		source_name,
				{
			"Patient Appointment": {
				"doctype": "Prescrizione lenti",
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

