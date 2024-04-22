import frappe
from frappe import _
from frappe.desk.page.setup_wizard import setup_wizard

@frappe.whitelist()
def setup_complete(args):
    response = setup_wizard.setup_complete(args)
    apply_fixtures(args)
    return response


def apply_fixtures(args):
    #group_medico = {"doctype": "Customer Group","customer_group_name":"Medico,", "is_group": 0, "old_parent": "Tutti i gruppi di clienti", "parent_customer_group": "Tutti i gruppi di clienti"}
    #frappe.get_doc(group_medico).insert()
    
    doc = frappe.get_doc('Selling Settings')
    doc.cust_master_name ="Naming Series"
    doc.save(ignore_permissions=True)
    
    m_p = {"doctype": "Mode of Payment", "mode_of_payment": "Bancomat", "type": "Bank", "mode_of_payment_code": "MP05-Bonifico"}
    frappe.get_doc(m_p).insert()

    mode_of_payments =[
		{"doctype": "Mode of Payment", "mode_of_payment": _("Cheque"),"type": "Bank","mode_of_payment_code":"MP02-Assegno",},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Cash"), "type": "Cash", "mode_of_payment_code": "MP01-Contanti"},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Credit Card"), "type": "Bank", "mode_of_payment_code": "MP08-Carta di pagamento"},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Wire Transfer"), "type": "Bank", "mode_of_payment_code": "MP05-Bonifico"},
		{"doctype": "Mode of Payment", "mode_of_payment": _("Bank Draft"), "type": "Bank", "mode_of_payment_code": "MP02-Assegno"},
    ]
    

    for m_p in mode_of_payments:
        try:
            doc = frappe.get_doc("Mode of Payment", m_p["mode_of_payment"])
            doc.type = m_p["type"]
            doc.mode_of_payment_code = m_p["mode_of_payment_code"]
            doc.save()
        except frappe.DoesNotExistError:
            pass




    ''' 
    {"doctype": "Tax Rule","customer_group":"Medico",
      "company":"DEF_COMPANY", "sales_tax_template":"Italy Tax -V",
      "shipping_country":"Italy", "tax_type":"Sales", "use_for_shopping_cart":1
    }
    '''


    

