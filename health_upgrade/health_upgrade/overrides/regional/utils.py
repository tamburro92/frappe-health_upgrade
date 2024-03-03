import io
import json

import frappe
from frappe import _
from frappe.utils import cstr, flt
from frappe.utils.file_manager import remove_file

from erpnext.controllers.taxes_and_totals import get_itemised_tax
from erpnext.regional.italy import state_codes

from erpnext.regional.italy.utils import get_company_country, get_progressive_name_and_number, prepare_invoice, get_e_invoice_attachments

# Ensure payment details are valid for e-invoice.
def sales_invoice_on_submit(doc, method):
	# Validate payment details
	if get_company_country(doc.company) not in [
		"Italy",
		"Italia",
		"Italian Republic",
		"Repubblica Italiana",
	]:
		return

	if not len(doc.payment_schedule):
		frappe.throw(_("Please set the Payment Schedule"), title=_("E-Invoicing Information Missing"))
	else:
		for schedule in doc.payment_schedule:
			if not schedule.mode_of_payment:
				frappe.throw(
					_("Row {0}: Please set the Mode of Payment in Payment Schedule").format(schedule.idx),
					title=_("E-Invoicing Information Missing"),
				)
			elif not frappe.db.get_value(
				"Mode of Payment", schedule.mode_of_payment, "mode_of_payment_code"
			):
				frappe.throw(
					_("Row {0}: Please set the correct code on Mode of Payment {1}").format(
						schedule.idx, schedule.mode_of_payment
					),
					title=_("E-Invoicing Information Missing"),
				)

	prepare_and_attach_invoice(doc)


def prepare_and_attach_invoice(doc, replace=False):
	#check if exists older xml then remove
	attachment_name = ""
	for attachment in get_e_invoice_attachments(doc):
		attachment_name = attachment.file_name[:-4]
		remove_file(attachment.name, attached_to_doctype=doc.doctype, attached_to_name=doc.name)

	if attachment_name:
		progressive_name, progressive_number = attachment_name, attachment_name.split("_")[1]
	else:
		progressive_name, progressive_number = get_progressive_name_and_number(doc, replace)
	
	invoice = prepare_invoice(doc, progressive_number)
	item_meta = frappe.get_meta("Sales Invoice Item")
	
	invoice_xml = frappe.render_template(
		"health_upgrade/health_upgrade/overrides/regional/e-invoice_custom.xml",
		context={"doc": invoice, "item_meta": item_meta},
		is_path=True,
	)

	invoice_xml = invoice_xml.replace("&", "&amp;")

	xml_filename = progressive_name + ".xml"

	_file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": xml_filename,
			"attached_to_doctype": doc.doctype,
			"attached_to_name": doc.name,
			"is_private": True,
			"content": invoice_xml,
		}
	)
	_file.save()
	return _file


@frappe.whitelist()
def generate_single_invoice(docname):
	doc = frappe.get_doc("Sales Invoice", docname)
	frappe.has_permission("Sales Invoice", doc=doc, throw=True)

	e_invoice = prepare_and_attach_invoice(doc, True)
	return e_invoice.file_url