import frappe
from erpnext.setup.utils import insert_record
from frappe import _


def setup_health_upgrade():

	create_custom_records()
	frappe.clear_cache()


def create_custom_records():
	setup_patient_history_settings()
	setup_healthcare_settings()


def setup_healthcare_settings():
	settings = frappe.get_single("Healthcare Settings")
	settings.patient_name_by = "Naming Series"
	settings.link_customer_to_patient = 1

	settings.save()

def setup_patient_history_settings():
	import json

	settings = frappe.get_single("Patient History Settings")
	configuration = get_patient_history_config()
	for dt, config in configuration.items():
		settings.append(
			"standard_doctypes",
			{"document_type": dt, "date_fieldname": config[0], "selected_fields": json.dumps(config[1])},
		)
	settings.save()


def get_patient_history_config():
	return {
		"Procedura Oculistica": (
			"encounter_date",
			[
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},
				
				{"label": "Interventi", "fieldname": "interventi", "fieldtype": "Small Text"},
				{"label": "Amnesi Generale", "fieldname": "amnesi_generale", "fieldtype": "Small Text"},
				{"label": "Amnesi Oculare", "fieldname": "amnesi_oculare", "fieldtype": "Small Text"},
				{"label": "Amnesi Ortottica", "fieldname": "amnesi_ortottica", "fieldtype": "Small Text"},
				{"label": "Esame Obiettivo", "fieldname": "esame_obiettivo", "fieldtype": "Small Text"},
				{"label": "Referti Esami", "fieldname": "referti_esami", "fieldtype": "Small Text"},
				{"label": "Diagnosi", "fieldname": "diagnosi", "fieldtype": "Small Text"},
				{"label": "Indicazioni", "fieldname": "indicazioni", "fieldtype": "Small Text"},
				{"label": "Diario", "fieldname": "diario", "fieldtype": "Small Text"},
			],
		),
		"Prescrizione Lenti": (
			"encounter_date",
			[
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},

				],
		)
	}
