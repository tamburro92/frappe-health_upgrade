# Copyright (c) 2023, Tamburro and contributors
# For license information, please see license.txt


import frappe
from frappe import _, msgprint
from frappe.model.meta import get_field_precision
from frappe.utils import flt

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimension_with_children,
)
from erpnext.accounts.report.utils import get_query_columns, get_values_for_columns


def execute(filters=None):
	return _execute(filters)


def _execute(filters, additional_table_columns=None):
	if not filters:
		filters = frappe._dict({})

	invoice_list = get_invoices(filters, get_query_columns(additional_table_columns))
	columns= get_columns()

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list


	#company_currency = frappe.get_cached_value("Company", filters.get("company"), "default_currency")
	#mode_of_payments = get_mode_of_payments([inv.name for inv in invoice_list])

	item_rate_map = get_item_rate_map(filters.healthcare_practitioner)

	invoice_ic_ig_in_map = get_invoice_ic_ig_in_map(invoice_list)
	
	data = []
	expenses_t, payment_amount_t, room_charge_amount_t, doctor_amount_t = 0, 0, 0, 0
	for inv in invoice_list:
		
		# invoice details	
		item_code = invoice_ic_ig_in_map.get(inv.name, {}).get("item_code", [])
		item_group = invoice_ic_ig_in_map.get(inv.name, {}).get("item_group", [])
		item_name = invoice_ic_ig_in_map.get(inv.name, {}).get("item_name", [])
		item_base_net_amount = invoice_ic_ig_in_map.get(inv.name, {}).get("base_net_amount", [])

		for i in range(len(item_code)):
			item_rate = item_rate_map.get(item_group[i],0) if item_group else 0
			item_amount = item_base_net_amount[i]

			#Compute expenses only 1 time
			expenses_p = 0
			if i == 0:
				expenses_t += inv.hc_expenses
				expenses_p = inv.hc_expenses

			room_charge_amount = item_rate / 100 * (item_amount - expenses_p)

			doctor_amount = item_amount - room_charge_amount
			row = {
				'date': inv.posting_date if i==0 else "",
				"customer_name": inv.customer_name if i==0 else "***",
				"patient_name": inv.patient if i==0 else "",
				"doctor_name": inv.company if i==0 else "",
				"payment_amount": item_amount,
				"expenses": expenses_p,
				"room_charge_percentage": item_rate,
				"room_charge_amount": room_charge_amount,
				"doctor_amount": doctor_amount,
				"invoice_name": inv.name
			}

			payment_amount_t += item_amount
			room_charge_amount_t += room_charge_amount
			doctor_amount_t += doctor_amount

			data.append(row)

	data.append({
		"nominativo_paziente": "Totale",
		"expenses" : expenses_t,
		"payment_amount": payment_amount_t,
		"room_charge_amount" : room_charge_amount_t,
		"doctor_amount" : doctor_amount_t
	})
	data.append({
		"room_charge_percentage": "<b>Totale</b>",
		"doctor_amount" : doctor_amount_t
	})

	return columns, data


def get_columns():
	"""return columns based on filters"""
	columns = [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Nominativo Cliente"),
			"fieldname": "customer_name",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"label": _("Medico"),
			"fieldname": "doctor_name",
			"fieldtype": "Link",
			"options": "Healthcare Practitioner",
			"width": 150
		},
		{
			"label": _("Fattura"),
			"fieldname": "invoice_name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 200
		},
		{
			"label": _("Importo Pagato"),
			"fieldname": "payment_amount",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Spese"),
			"fieldname": "expenses",
			"fieldtype": "Currency",
			"width": 75
		},
		{
			"label": _("% Studio"),
			"fieldname": "room_charge_percentage",
			"fieldtype": "Data",
			"width": 75
		},
		{
			"label": _("Importo Studio"),
			"fieldname": "room_charge_amount",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Importo Medico + spese"),
			"fieldname": "doctor_amount",
			"fieldtype": "Currency",
			"width": 200
		},
	]


	return columns


def get_conditions(filters):
	conditions = ""

	accounting_dimensions = get_accounting_dimensions(as_list=False) or []
	accounting_dimensions_list = [d.fieldname for d in accounting_dimensions]

	if filters.get("company"):
		conditions += " and company=%(company)s"

	if filters.get("customer") and "customer" not in accounting_dimensions_list:
		conditions += " and customer = %(customer)s"

	if filters.get("from_date"):
		conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and posting_date <= %(to_date)s"

	if filters.get("owner"):
		conditions += " and owner = %(owner)s"

	if filters.get("healthcare_practitioner"):
		conditions += " and hc_practitioner = %(healthcare_practitioner)s"

	def get_sales_invoice_item_field_condition(field, table="Sales Invoice Item") -> str:
		if not filters.get(field) or field in accounting_dimensions_list:
			return ""
		return f""" and exists(select name from `tab{table}`
				where parent=`tabSales Invoice`.name
					and ifnull(`tab{table}`.{field}, '') = %({field})s)"""

	conditions += get_sales_invoice_item_field_condition("mode_of_payment", "Sales Invoice Payment")
	conditions += get_sales_invoice_item_field_condition("cost_center")
	conditions += get_sales_invoice_item_field_condition("warehouse")
	conditions += get_sales_invoice_item_field_condition("brand")
	conditions += get_sales_invoice_item_field_condition("item_group")

	if accounting_dimensions:
		common_condition = """
			and exists(select name from `tabSales Invoice Item`
				where parent=`tabSales Invoice`.name
			"""
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value("DocType", dimension.document_type, "is_tree"):
					filters[dimension.fieldname] = get_dimension_with_children(
						dimension.document_type, filters.get(dimension.fieldname)
					)

					conditions += (
						common_condition
						+ "and ifnull(`tabSales Invoice`.{0}, '') in %({0})s)".format(dimension.fieldname)
					)
				else:
					conditions += (
						common_condition
						+ "and ifnull(`tabSales Invoice`.{0}, '') in %({0})s)".format(dimension.fieldname)
					)

	return conditions

def get_item_rate_map(practitioner_id):
	practitioner = frappe.get_doc("Healthcare Practitioner", practitioner_id)

	item_rate_map = {}
	for item in practitioner.hc_item_groups:
		item_rate_map[item.item_group] = item.rate

	return item_rate_map

def get_invoices(filters, additional_query_columns):
	conditions = get_conditions(filters)
	return frappe.db.sql(
		"""
		select name, posting_date, debit_to, project, customer,
		customer_name, owner, remarks, territory, tax_id, customer_group,
		base_net_total, base_grand_total, base_rounded_total, outstanding_amount,
		is_internal_customer, represents_company, company, hc_expenses, hc_practitioner, patient {0}
		from `tabSales Invoice`
		where docstatus = 1 {1}
		order by posting_date desc, name desc""".format(
			additional_query_columns, conditions
		),
		filters,
		as_dict=1,
	)


def get_invoice_income_map(invoice_list):
	income_details = frappe.db.sql(
		"""select parent, income_account, sum(base_net_amount) as amount
		from `tabSales Invoice Item` where parent in (%s) group by parent, income_account"""
		% ", ".join(["%s"] * len(invoice_list)),
		tuple(inv.name for inv in invoice_list),
		as_dict=1,
	)

	invoice_income_map = {}
	for d in income_details:
		invoice_income_map.setdefault(d.parent, frappe._dict()).setdefault(d.income_account, [])
		invoice_income_map[d.parent][d.income_account] = flt(d.amount)

	return invoice_income_map


def get_internal_invoice_map(invoice_list):
	unrealized_amount_details = frappe.db.sql(
		"""SELECT name, unrealized_profit_loss_account,
		base_net_total as amount from `tabSales Invoice` where name in (%s)
		and is_internal_customer = 1 and company = represents_company"""
		% ", ".join(["%s"] * len(invoice_list)),
		tuple(inv.name for inv in invoice_list),
		as_dict=1,
	)

	internal_invoice_map = {}
	for d in unrealized_amount_details:
		if d.unrealized_profit_loss_account:
			internal_invoice_map.setdefault((d.name, d.unrealized_profit_loss_account), d.amount)

	return internal_invoice_map


def get_invoice_tax_map(invoice_list, invoice_income_map, income_accounts):
	tax_details = frappe.db.sql(
		"""select parent, account_head,
		sum(base_tax_amount_after_discount_amount) as tax_amount
		from `tabSales Taxes and Charges` where parent in (%s) group by parent, account_head"""
		% ", ".join(["%s"] * len(invoice_list)),
		tuple(inv.name for inv in invoice_list),
		as_dict=1,
	)

	invoice_tax_map = {}
	for d in tax_details:
		if d.account_head in income_accounts:
			if d.account_head in invoice_income_map[d.parent]:
				invoice_income_map[d.parent][d.account_head] += flt(d.tax_amount)
			else:
				invoice_income_map[d.parent][d.account_head] = flt(d.tax_amount)
		else:
			invoice_tax_map.setdefault(d.parent, frappe._dict()).setdefault(d.account_head, [])
			invoice_tax_map[d.parent][d.account_head] = flt(d.tax_amount)

	return invoice_income_map, invoice_tax_map


def get_invoice_ic_ig_in_map(invoice_list):
	si_items = frappe.db.sql(
		"""select parent, item_code, item_group, item_name, base_amount, base_net_amount, base_net_rate, base_price_list_rate, base_rate
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(item_code, '') != '' or ifnull(item_group, '') != '' or ifnull(item_name, '') != '')"""
		% ", ".join(["%s"] * len(invoice_list)),
		tuple(inv.name for inv in invoice_list),
		as_dict=1,
	)
	invoice_ic_ig_in_map = {}
	for d in si_items:
		if d.item_code:
			invoice_ic_ig_in_map.setdefault(d.parent, frappe._dict()).setdefault("item_code", []).append(
				d.item_code
			)

		if d.item_group:
			invoice_ic_ig_in_map.setdefault(d.parent, frappe._dict()).setdefault("item_group", []).append(
				d.item_group
			)
		if d.item_name:
			invoice_ic_ig_in_map.setdefault(d.parent, frappe._dict()).setdefault("item_name", []).append(
				d.item_name
			)
		if d.base_net_amount:
			invoice_ic_ig_in_map.setdefault(d.parent, frappe._dict()).setdefault("base_net_amount", []).append(
				d.base_net_amount
			)

	return invoice_ic_ig_in_map


def get_invoice_so_dn_map(invoice_list):
	si_items = frappe.db.sql(
		"""select parent, sales_order, delivery_note, so_detail
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(sales_order, '') != '' or ifnull(delivery_note, '') != '')"""
		% ", ".join(["%s"] * len(invoice_list)),
		tuple(inv.name for inv in invoice_list),
		as_dict=1,
	)

	invoice_so_dn_map = {}
	for d in si_items:
		if d.sales_order:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault("sales_order", []).append(
				d.sales_order
			)

		delivery_note_list = None
		if d.delivery_note:
			delivery_note_list = [d.delivery_note]
		elif d.sales_order:
			delivery_note_list = frappe.db.sql_list(
				"""select distinct parent from `tabDelivery Note Item`
				where docstatus=1 and so_detail=%s""",
				d.so_detail,
			)

		if delivery_note_list:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault(
				"delivery_note", delivery_note_list
			)

	return invoice_so_dn_map


def get_invoice_cc_wh_map(invoice_list):
	si_items = frappe.db.sql(
		"""select parent, cost_center, warehouse
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(cost_center, '') != '' or ifnull(warehouse, '') != '')"""
		% ", ".join(["%s"] * len(invoice_list)),
		tuple(inv.name for inv in invoice_list),
		as_dict=1,
	)

	invoice_cc_wh_map = {}
	for d in si_items:
		if d.cost_center:
			invoice_cc_wh_map.setdefault(d.parent, frappe._dict()).setdefault("cost_center", []).append(
				d.cost_center
			)

		if d.warehouse:
			invoice_cc_wh_map.setdefault(d.parent, frappe._dict()).setdefault("warehouse", []).append(
				d.warehouse
			)

	return invoice_cc_wh_map


def get_mode_of_payments(invoice_list):
	mode_of_payments = {}
	if invoice_list:
		inv_mop = frappe.db.sql(
			"""select parent, mode_of_payment
			from `tabSales Invoice Payment` where parent in (%s) group by parent, mode_of_payment"""
			% ", ".join(["%s"] * len(invoice_list)),
			tuple(invoice_list),
			as_dict=1,
		)

		for d in inv_mop:
			mode_of_payments.setdefault(d.parent, []).append(d.mode_of_payment)

	return mode_of_payments
