# Copyright (c) 2023, Tamburro and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_data(values):
	data = frappe.db.sql("""
        SELECT
			a.appointment_date, a.appointment_time, a.duration, a.patient_name, a.hc_procedure_name,
			a.practitioner_name, a.notes, a.hc_requires_nurse, a.hc_requires_anaesthetist, a.patient,
			contact.phone, contact.mobile_no
		FROM `tabPatient Appointment` AS a
			LEFT JOIN `tabPatient` AS p
			ON a.patient = p.name
			LEFT JOIN `tabCustomer` AS c
			ON p.customer = c.name
			LEFT JOIN `tabDynamic Link` AS link
			ON link.link_name = c.name
			LEFT JOIN `tabContact` AS contact
			ON contact.name=link.parent				  
		WHERE a.appointment_date = %(date)s
		    AND contact.is_primary_contact = 1

		UNION

		SELECT
			a.appointment_date, a.appointment_time, a.duration, a.patient_name, a.hc_procedure_name,
			a.practitioner_name, a.notes, a.hc_requires_nurse, a.hc_requires_anaesthetist, a.patient,
			NULL AS phone, NULL AS mobile_no
		FROM `tabPatient Appointment` AS a	  
		WHERE a.appointment_date = %(date)s AND a.name NOT IN(
            SELECT
                a.name
            FROM `tabPatient Appointment` AS a
                LEFT JOIN `tabPatient` AS p
                ON a.patient = p.name
                LEFT JOIN `tabCustomer` AS c
                ON p.customer = c.name
                LEFT JOIN `tabDynamic Link` AS link
                ON link.link_name = c.name
                LEFT JOIN `tabContact` AS contact
                ON contact.name=link.parent				  
            WHERE a.appointment_date = %(date)s
                AND contact.is_primary_contact = 1)
	    ORDER BY appointment_time ASC 
	""", values=values, as_dict=1)	
	return data

def get_data_fast(filters):
	entries = frappe.db.get_all(
		"Patient Appointment",
		fields=["appointment_date", "appointment_time", "duration", "patient_name", "hc_procedure_name",
		    "practitioner_name", "notes", "hc_requires_nurse", "hc_requires_anaesthetist"],
		filters={'appointment_date': filters.date})
	
	return entries
def get_columns():
	"""return columns based on filters"""
	columns = [
            {
                "label": "Data",
                "fieldname": "appointment_date",
                "fieldtype": "Date",
                "width": 100
            },
            {
                "label": "Tempo",
                "fieldname": "appointment_time",
                "fieldtype": "Time",
                "width": 80
            },
            {
                "label": "Durata",
                "fieldname": "duration",
                "fieldtype": "Int",
                "width": 80
            },
            {
                "label": "Paziente",
                "fieldname": "patient_name",
                "fieldtype": "Data",
                "width": 200
            },
            {
                "label": "servizio",
                "fieldname": "hc_procedure_name",
                "fieldtype": "Data",
                "width": 300
            },
            {
                "label": "Telefono",
                "fieldname": "phone",
                "fieldtype": "Data",
                "width": 100
            },
			{
                "label": "Mobile",
                "fieldname": "mobile_no",
                "fieldtype": "Data",
                "width": 100
            },
            {
                "label": "Practitioner",
                "fieldname": "practitioner_name",
                "fieldtype": "Data",
                "options": "Healthcare Practitioner",
                "width": 150
            },
            {
                "label": "Note",
                "fieldname": "notes",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": "Richiesta Infermiera",
                "fieldname": "hc_requires_nurse",
                "fieldtype": "Check",
                "width": 80
            },
			{
                "label": "Richiesta Anestetista",
                "fieldname": "hc_requires_anaesthetist",
                "fieldtype": "Check",
                "width": 80
            },
            {
                "label": "Sovrapposto a",
                "fieldname": "overlaps_with",
                "fieldtype": "HTML",
                "width": 150
            }
        ]

	return columns
