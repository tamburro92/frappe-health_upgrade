import frappe
from erpnext.setup.utils import insert_record
from frappe import _

def setup_health_upgrade():
	create_custom_records()
	frappe.clear_cache()


def create_custom_records():
	setup_erpnext_settings()
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
		"Visita oculistica": (
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
		"Prescrizione lenti": (
			"encounter_date",
			[
				{"label": "Healthcare Practitioner", "fieldname": "practitioner", "fieldtype": "Link"},

				],
		)
	}


def setup_erpnext_settings():
    lang = 'it'

    doc = frappe.get_doc('Selling Settings')
    doc.cust_master_name ="Naming Series"
    doc.save()
    
    m_p = {"doctype": "Mode of Payment", "mode_of_payment": "Bancomat", "type": "Bank", "mode_of_payment_code": "MP05-Bonifico"}
    m_p_doc = frappe.get_doc(m_p)
    m_p_doc.insert(ignore_if_duplicate = True)

    mode_of_payments =[
		{"doctype": "Mode of Payment", "mode_of_payment": _("Cheque", lang),"type": "Bank","mode_of_payment_code":"MP02-Assegno",},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Cash", lang), "type": "Cash", "mode_of_payment_code": "MP01-Contanti"},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Credit Card", lang), "type": "Bank", "mode_of_payment_code": "MP08-Carta di pagamento"},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Wire Transfer", lang), "type": "Bank", "mode_of_payment_code": "MP05-Bonifico"},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Bank Draft", lang), "type": "Bank", "mode_of_payment_code": "MP02-Assegno"},
    ]
    

    for m_p in mode_of_payments:
        try:
            doc = frappe.get_doc("Mode of Payment", m_p["mode_of_payment"])
            doc.type = m_p["type"]
            doc.mode_of_payment_code = m_p["mode_of_payment_code"]
            doc.save()
        except frappe.DoesNotExistError as e:
            pass




    ''' 
    {"doctype": "Tax Rule","customer_group":"Medico",
      "company":"DEF_COMPANY", "sales_tax_template":"Italy Tax -V",
      "shipping_country":"Italy", "tax_type":"Sales", "use_for_shopping_cart":1
    }
    '''

