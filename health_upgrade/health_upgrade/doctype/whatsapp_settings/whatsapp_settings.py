# Copyright (c) 2024, Tamburro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import json

WHATS_APP_API = 'https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages'
WHATS_APP_DATA = '''{
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": "{PHONE_NUMBER}",
      "type": "text",
      "text": { 
        "preview_url": true,
        "body": "{MESSAGE_CONTENT}"
        }
    }'''

class WhatsAppSettings(Document):
	pass


def validate_receiver_nos(receiver_list):
	validated_receiver_list = []
	for d in receiver_list:
		if not d:
			continue

		# remove invalid character
		for x in [" ", "-", "(", ")"]:
			d = d.replace(x, "")

		validated_receiver_list.append(d)

	if not validated_receiver_list:
		throw(_("Please enter valid mobile nos"))

	return validated_receiver_list


@frappe.whitelist()
def get_contact_number(contact_name, ref_doctype, ref_name):
	"returns mobile number of the contact"
	number = frappe.db.sql(
		"""select mobile_no, phone from tabContact
		where name=%s
			and exists(
				select name from `tabDynamic Link` where link_doctype=%s and link_name=%s
			)
	""",
		(contact_name, ref_doctype, ref_name),
	)

	return number and (number[0][0] or number[0][1]) or ""


@frappe.whitelist()
def send_whatsapp_sms(receiver_list, msg, sender_name="", success_msg=True):
	import json

	if isinstance(receiver_list, str):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	receiver_list = validate_receiver_nos(receiver_list)

	arg = {
		"receiver_list": receiver_list,
		"message": frappe.safe_decode(msg).encode("utf-8"),
		"success_msg": success_msg,
	}

	send_via_api(arg)


def send_via_api(arg):
	ss = frappe.get_doc("WhatsApp Settings", "WhatsApp Settings")
	
	headers = {}
	headers['Content-Type'] = 'application/json'
	headers['Authorization'] = 'Bearer ' + ss.access_token
	
	message = frappe.safe_decode(arg.get("message"))
	
	args = {}


	success_list = []
	for phone_number in arg.get("receiver_list"):

		url = WHATS_APP_API.format(PHONE_NUMBER_ID=ss.phone_number_id)
		data = json.loads(WHATS_APP_DATA)
		if not phone_number.startswith('+'):
			phone_number = '+39'+ phone_number
		data['to'] = phone_number
		data['text']['body'] = message
		status = send_request(url, headers, data)

		if 200 <= status < 300:
			success_list.append(phone_number)

	if len(success_list) > 0:
		args.update(arg)
		#create_whatsapp_log(args, success_list)
		if arg.get("success_msg"):
			frappe.msgprint(_("WhatsApp message sent to following numbers: {0}").format("\n" + "\n".join(success_list)))


def send_request(url, headers, data):
	import requests

	response = requests.post(url, headers=headers, json=data)

	response.raise_for_status()
	return response.status_code


# Create WhatsApp Log
# =========================================================
def create_whatsapp_log(args, sent_to):
	sl = frappe.new_doc("SMS Log")
	sl.sent_on = nowdate()
	sl.message = args["message"].decode("utf-8")
	sl.no_of_requested_sms = len(args["receiver_list"])
	sl.requested_numbers = "\n".join(args["receiver_list"])
	sl.no_of_sent_sms = len(sent_to)
	sl.sent_to = "\n".join(sent_to)
	sl.flags.ignore_permissions = True
	sl.save()
