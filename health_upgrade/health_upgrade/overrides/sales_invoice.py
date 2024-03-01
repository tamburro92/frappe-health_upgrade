
import frappe
from healthcare.healthcare.custom_doctype.sales_invoice import HealthcareSalesInvoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from erpnext.regional.italy.utils import get_progressive_name_and_number, prepare_invoice
from frappe.utils import get_url
from frappe.utils.pdf import get_pdf
from frappe.utils.print_format import download_pdf
from frappe.www.printview import validate_print_permission
from frappe.translate import print_language
import json 
import zipfile
from zipimport import zipimporter, ZipImportError
from io import BytesIO
import time
from frappe.email.email_body import get_filecontent_from_path

class SalesInvoiceHC(HealthcareSalesInvoice):
	def validate(self):
		super(HealthcareSalesInvoice, self).validate()
		
		for p in self.payment_schedule:
			if not p.mode_of_payment and self.hc_mode_of_payment:
				p.mode_of_payment = self.hc_mode_of_payment
				p.mode_of_payment_code = frappe.get_value("Mode of Payment", self.hc_mode_of_payment, "mode_of_payment_code")

	def on_submit(self):
		super(HealthcareSalesInvoice, self).on_submit()
		pe = get_payment_entry(dt="Sales Invoice", dn=self.name)
		pe.save()
		pe.submit()
		self.notify_update()



@frappe.whitelist()
def download_sales_invoices(args):													  
	args = json.loads(args)
	invoices = frappe.db.get_list('Sales Invoice', as_list=True,
    filters=[
		['posting_date', 'between', args['date'] ],
		['docstatus', '=', '1'],
		['company', '=', args['company'] ]
		])
	
	company_doc = frappe.get_doc("Company",args['company'])
	letterhead = company_doc.get('default_letter_head')
	format = company_doc.get('default_print_company')
	abbr = company_doc.get('abbr')

	files = []
	for i in range(len(invoices)):
		name = invoices[i][0]
		frappe.publish_progress(i*100/len(invoices), title='Download Sales Invoices', description='Elaborating {}...'.format(name))
		doc = frappe.get_doc("Sales Invoice",name)
		#data_xml, name_xml  = create_xml(doc)
		data_xml, name_xml  = retrieve_xml(doc)
		data_pdf = create_pdf(doc, name, format=format, doc=None, no_letterhead=0, language=None, letterhead=letterhead)
		name_pdf = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
		if data_xml and name_xml:
			files.append([name_xml,data_xml])
		if name_pdf and data_pdf:
			files.append([name_pdf,data_pdf])

	frappe.publish_progress(100, title='Download Sales Invoices', description='Creating Zip...')
	zip_filename = "{}-SINV-{}.zip".format(abbr,
		frappe.utils.data.format_datetime(frappe.utils.now(), "Ymd_HMs")
	)
	mem_zip = BytesIO()
	with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
		for f in files:
			zf.writestr(f[0], f[1])
	
	_file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": zip_filename,
			"content": mem_zip.getvalue(),
			"is_private": 1,
		}
	)
	_file.save(ignore_permissions=True)
	file_url = _file.file_url

	frappe.msgprint('<a href="{}" target="_blank">Click here to download ZIP</a>'.format(file_url))


	
def retrieve_xml(doc):
	filename = ""
	file_url = ""
	for attachment in get_e_invoice_attachments(doc):
		filename = attachment.file_name
		file_url = attachment.file_url
		break
	xml_data = get_filecontent_from_path(file_url)
	
	return xml_data, filename

def create_pdf(doctype, name, format=None, doc=None, no_letterhead=0, language=None, letterhead=None):
	doc = doc or frappe.get_doc(doctype, name)
	validate_print_permission(doc)

	with print_language(language):
		pdf_file = frappe.get_print(doctype, name, format, doc=doc, as_pdf=True, letterhead=letterhead, no_letterhead=no_letterhead)

	return pdf_file

def create_xml(doc):
	progressive_name, progressive_number = get_progressive_name_and_number(doc, False)

	invoice = prepare_invoice(doc, progressive_number)
	item_meta = frappe.get_meta("Sales Invoice Item")

	invoice_xml = frappe.render_template(
		"",
		context={"doc": invoice, "item_meta": item_meta},
		is_path=True,
	)

	invoice_xml = invoice_xml.replace("&", "&amp;")

	xml_filename = progressive_name + ".xml"
	return invoice_xml, xml_filename

def get_e_invoice_attachments(invoices):
	if not isinstance(invoices, list):
		if not invoices.company_tax_id:
			return

		invoices = [invoices]

	tax_id_map = {
		invoice.name: (
			invoice.company_tax_id
			if invoice.company_tax_id.startswith("IT")
			else "IT" + invoice.company_tax_id
		)
		for invoice in invoices
	}

	attachments = frappe.get_all(
		"File",
		fields=("name", "file_name", "attached_to_name", "is_private", "file_url"),
		filters={"attached_to_name": ("in", tax_id_map), "attached_to_doctype": "Sales Invoice"},
	)

	out = []
	for attachment in attachments:
		if (
			attachment.file_name
			and attachment.file_name.endswith(".xml")
			and attachment.file_name.startswith(tax_id_map.get(attachment.attached_to_name))
		):
			out.append(attachment)

	return out


# Overrides in hooks prepare_and_attach_invoice to use item price net
def prepare_and_attach_invoice(doc, replace=False):
	progressive_name, progressive_number = get_progressive_name_and_number(doc, replace)

	invoice = prepare_invoice(doc, progressive_number)
	item_meta = frappe.get_meta("Sales Invoice Item")

	invoice_xml = frappe.render_template(
		"health_upgrade/health_upgrade/overrides/e-invoice_custom.xml",
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