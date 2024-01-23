import frappe
from healthcare.healthcare.doctype.patient.patient import Patient
from frappe.contacts.doctype.address.address import get_default_address

class PatientHC(Patient):

	#continue here override and make save address
	def on_update(self):
		super(PatientHC, self).on_update()
		if self.flags.is_new_doc and self.get("address_line1"):
			id_addr = get_default_address("Patient",self.get("name"))
			if id_addr:
				addr = frappe.get_doc("Address", id_addr)
				addr.append("links", dict(link_doctype="Customer", link_name=self.customer))
				addr.save()
		
		if self.flags.is_new_doc and self.customer:
			customer_doc = frappe.get_doc("Customer", self.customer)
			if self.first_name:
				customer_doc.first_name = self.first_name
			if self.last_name:
				customer_doc.last_name = self.last_name
			if self.dob:
				customer_doc.custom_date_of_birth = self.dob
			if self.get('fiscal_code'):
				customer_doc.fiscal_code = self.get('fiscal_code')
			if self.get('birth_place'):
				customer_doc.custom_place_of_birth = self.get('birth_place')
			customer_doc.save()




