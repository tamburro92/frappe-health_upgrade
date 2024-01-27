import frappe
from erpnext.setup.doctype.company.company import Company
from erpnext.setup.setup_wizard.operations.taxes_setup import from_detailed_data, update_regional_tax_settings
#from erpnext.patches.v11_0.refactor_naming_series import set_series , get_series_to_preserve
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
import copy

NAMING_SERIES = "SINV-{}-.YYYY.-.#####."
NAMING_SERIES_RETURN = "SINV-RET-{}-.YYYY.-.#####."
class CompanyHC(Company):
	def after_insert(self):
		if not self.hc_naming_series:
			self.hc_naming_series = NAMING_SERIES.format(self.abbr)
		if not self.hc_naming_series_return:
			self.hc_naming_series_return = NAMING_SERIES_RETURN.format(self.abbr)
		self.default_letter_head = create_new_letter_head(self)
		self.save()

		append_series_to_invoice([self.hc_naming_series, self.hc_naming_series_return])

	@frappe.whitelist()
	def create_default_tax_template(self):
		# Don't Create default tax template, instead use custom
		# for bollo/non_bollo settings came from "Company HC Settings"
		# for Italy Tax, should be defined a "Tax Rule" binded to Customer
		super().create_default_tax_template()        
		from_detailed_data(self.name, copy.deepcopy(vat_bollo_nobollo))
		update_regional_tax_settings(self.country, self.name)

def create_new_letter_head(args):
	if not frappe.db.exists('Letter Head', args.get('name')):
		letter_head = frappe.get_doc({
			"doctype": "Letter Head",
			"letter_head_name": args.get("name")
		}).insert()
	return args.get('name')


def append_series_to_invoice(series):
	origina_series = get_series("Sales Invoice")
	updated_series = (list(set(origina_series + series)))
	updated_series.sort()
	set_series("Sales Invoice", "\n".join(updated_series), None)


def set_series(doctype, options, default):
	def _make_property_setter(property_name, value):
		property_setter = frappe.db.exists(
			"Property Setter",
			{"doc_type": doctype, "field_name": "naming_series", "property": property_name},
		)
		if property_setter:
			frappe.db.set_value("Property Setter", property_setter, "value", value)
		else:
			make_property_setter(doctype, "naming_series", "options", value, "Text")

	_make_property_setter("options", options)
	if default:
		_make_property_setter("default", default)

def get_series(doctype):
	series_to_preserve = []
	property_setter = frappe.db.exists(
		"Property Setter",
		{"doc_type": doctype, "field_name": "naming_series", "property": "options"},
	)
	if property_setter:
		series_to_preserve_s =  frappe.get_value("Property Setter", property_setter,"value")
		series_to_preserve = series_to_preserve_s.split("\n")
	else:
		series_to_preserve = frappe.db.sql_list(
		"""select distinct naming_series from `tab{doctype}` where ifnull(naming_series, '') != ''""".format(
			doctype=doctype
		))
	series_to_preserve.sort()
	return series_to_preserve



vat_bollo_nobollo = {
		"chart_of_accounts": {
			"*": {
				"item_tax_templates": [
					{
						"title": "VAT",
						"taxes": [
							{"tax_type": {"account_name": "VAT", "tax_rate": 22}}
						],
					},
					{
						"title": "Bollo",
						"taxes": [
							{"tax_type": {"account_name": "Bollo", "tax_rate": 0}}
						],
					}
				],
				"*": [
					{
						"title": "Bollo",
						"is_default": 0,
						"taxes": [
							{
								"account_head": {
									"account_name": "VAT",
								},
								"rate" : 0,
								"tax_exemption_reason":"N4-Esenti",
								"charge_type":"On Net Total",
								"description" : "VAT"
							},
							{
								"account_head": {
									"account_name": "Bollo"
								},
								"rate": 0,
								"tax_amount": 2,
								"charge_type":"Actual",
								"description" : "Bollo"
							}
						],
					},
					{
						"title": "Senza Bollo",
						"is_default": 0,
						"taxes": [
							{
								"account_head": {
									"account_name": "VAT",
								},
								"rate" : 0,
								"tax_exemption_reason":"N4-Esenti",
								"charge_type":"On Net Total",
								"description" : "VAT"
							}
						],
					},
					{
						"title": "Italy Tax",
						"is_default": 0,
						"taxes": [
							{
								"account_head": {
									"account_name": "VAT",
								},
								"rate" : 22,
								"included_in_print_rate": 1,
								"charge_type":"On Net Total",
								"description" :"VAT"
							}
						],
					},
				],
			}
		}
	}

'''
	frappe.db.sql(
		"""
		update `tabProperty Setter`
		set name=concat(doc_type, '-', field_name, '-', property)
		where property='fetch_from'
	"""
	)
'''