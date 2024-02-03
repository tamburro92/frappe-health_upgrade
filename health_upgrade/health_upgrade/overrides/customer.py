import frappe
from frappe import _
from erpnext.selling.doctype.customer.customer import Customer
from frappe.contacts.doctype.address.address import get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
import json

ADDRESS_FIELDS = ['custom_address_line_1','custom_address_line_2','custom_address_town','custom_pincode','custom_country', 'custom_state', 'custom_state_code']
CONTACT_FIELDS = ['custom_mobile','custom_email']

def handle_primary_contact(args):

	id_cont = get_default_contact("Customer",args.get("name"))
	if id_cont:
		cont = frappe.get_doc("Contact",id_cont)

		mod1 = update_email(cont, args)
		mod2 = update_mobile(cont, args)
		mod3 = update_phone(cont, args)

		if mod1 or mod2 or mod3 :
			cont.save()
	else:
		make_contact(args)


def update_email(cont, args):
	update = False
	email = args.get("custom_email", "")
	if cont.email_ids:
		if not email:
			cont.remove(cont.email_ids[0])
			update = True
		elif email != cont.email_ids[0].email_id:
			cont.email_ids[0].email_id = args.get("custom_email","")
			update = True
	if email and not update:
		cont.add_email(email, is_primary=True)
		update = True
	return update

def update_mobile(cont, args):
	update = False
	mobile = args.get("custom_mobile", "")
	if cont.phone_nos:
		for p in cont.phone_nos:
			if p.is_primary_mobile_no == 1:
				update = True
				if mobile:
					p.phone = mobile
				else:
					cont.remove(p)
	if mobile and not update:
		cont.add_phone(mobile, is_primary_mobile_no=True)
		update = True
	return update

def update_phone(cont, args):
	update = False
	phone = args.get("custom_phone", "")
	if cont.phone_nos:
		for p in cont.phone_nos:
			if p.is_primary_phone == 1:
				update = True
				if phone:
					p.phone = phone
				else:
					cont.remove(p)
	if phone and not update:
		cont.add_phone(phone, is_primary_phone=True)
		update = True
	return update


def handle_primary_address(args):
	skip_address = True
	for field in ADDRESS_FIELDS:
		if args.get(field):
			skip_address = False
	# handle if doc ad been created from quick editor and has beed compiled address we skip
	if skip_address: return

	id_addr = get_default_address("Customer",args.get("name"))
	if id_addr:
		addr = frappe.get_doc("Address",id_addr)
		addr.address_line1 = args.get("custom_address_line_1")
		addr.address_line2 = args.get("custom_address_line_2")
		addr.city = args.get("custom_address_town")
		addr.state = args.get("custom_state")
		addr.state_code = args.get("custom_state_code")
		addr.pincode = args.get("custom_pincode")
		addr.country = args.get("custom_country")
		addr.save()
	else:
		make_address(args)

def make_address(args, is_primary_address=1):
	address = frappe.get_doc(
		{
			"doctype": "Address",
			"address_title": args.get("name"),
			"address_line1": args.get("custom_address_line_1"),
			"address_line2": args.get("custom_address_line_2"),
			"city": args.get("custom_address_town"),
			"state": args.get("custom_state"),
			"state_code": args.get("custom_state_code"),
			"pincode": args.get("custom_pincode"),
			"country": args.get("custom_country"),
			"links": [{"link_doctype": "Customer", "link_name": args.get("name")}],
		}
	).insert()

	return address

def make_contact(args, is_primary_contact=1):
	contact = frappe.get_doc(
		{
			"doctype": "Contact",
			"first_name": args.get("name"),
			"is_primary_contact": is_primary_contact,
			"links": [{"link_doctype": "Customer", "link_name": args.get("name")}],
		}
	)

	if args.get("custom_email"):
		contact.add_email(args.get("custom_email"), is_primary=True)
	if args.get("custom_mobile"):
		contact.add_phone(args.get("custom_mobile"), is_primary_mobile_no=True)
	contact.insert()

	return contact


@frappe.whitelist()
def get_default_address_and_contact_data(doctype, name):
		response = {'address': None, 'contact': None} 
		id_addr = get_default_address(doctype, name)
		if id_addr: 
			response['address'] = frappe.get_doc("Address",id_addr)

		id_cont = get_default_contact(doctype, name)
		if id_cont: 
			response['contact'] = frappe.get_doc("Contact",id_cont)
		return response

@frappe.whitelist()
def set_default_address_and_contact_data(address, contact):
	handle_primary_address(json.loads(address))
	handle_primary_contact(json.loads(contact))
	
	#return success

