# Copyright (c) 2024, Tamburro and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class HCSettings(Document):
	def validate(self):
		self.validate_default_options()


	def validate_default_options(self):

		# set default values if empty in saving
		for df in self.meta.fields:
			if df.fieldname in ["appointment_reminder_msg_wa", "remind_before"]:
				if not self.get(df.fieldname):
					self.set(df.fieldname, df.default)
