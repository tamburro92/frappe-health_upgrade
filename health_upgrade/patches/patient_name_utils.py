import frappe
#from erpnext.selling.doctype.customer.customer import get_customer_name

#bench execute health_upgrade.patches.patient_name_utils.rename_patients_name
def rename_patients_name():
    doc_type = "Customer"
    customers = frappe.db.get_all(doc_type, pluck="name")
    for c in customers:
        customer = frappe.get_doc(doc_type, c)
        new_name = customer.get_customer_name()
        frappe.rename_doc(doc_type,c,new_name)
        print(f'step {c}')

    frappe.db.commit()

