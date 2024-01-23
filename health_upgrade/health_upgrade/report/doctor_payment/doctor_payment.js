// Copyright (c) 2023, Tamburro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Doctor Payment"] = {
	"filters": [
		{
			"fieldname":"healthcare_practitioner",
			"label": __("Doctor"),
			"fieldtype": "Link",
			"options": "Healthcare Practitioner",
			"reqd": 1
		},
		{
			"fieldname":"alternate_practitioner",
			"label": __("Alternate Doctor"),
			"fieldtype": "Link",
			"options": "Healthcare Practitioner"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		}
	]
}

erpnext.utils.add_dimensions('Sales Register', 7);