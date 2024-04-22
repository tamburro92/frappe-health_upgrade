import frappe
from frappe import _
from frappe.desk.page.setup_wizard import setup_wizard
from health_upgrade.setup import setup_erpnext_settings

@frappe.whitelist()
def setup_complete(args):
    response = setup_wizard.setup_complete(args)
    setup_erpnext_settings()
    return response