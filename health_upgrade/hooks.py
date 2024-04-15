from . import __version__ as app_version

app_name = "health_upgrade"
app_title = "Health Upgrade"
app_publisher = "Tamburro"
app_description = "Healhcare customization"
app_email = "t@"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/health_upgrade/css/health_upgrade.css"
app_include_js = "health_upgrade.bundle.js"

# include js, css files in header of web template
# web_include_css = "/assets/health_upgrade/css/health_upgrade.css"
# web_include_js = "/assets/health_upgrade/js/health_upgrade.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "health_upgrade/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {
    "print": "public/js/print.js"
    }

fixtures = [{
         "dt": "Custom Field", 
         "filters":[["module", "=", "Health Upgrade"]]
      },
      {
         "dt": "Property Setter", 
          "filters": [["name", "in", [ "Patient Appointment-appointment_type-reqd", 
                                      "Patient-sex-reqd", "Customer-defaults_tab-collapsible",
                                      "Practitioner Service Unit Schedule-Practitioner Service Unit Schedule-in_list_view",
                                      "Sales Invoice-service_unit-hidden", "Sales Invoice-ref_practitioner-hidden",
                                      "Patient-invite_user-default"
                                      ]]]
      },
      # { "dt": "Print Format", "filters": [["name", "in", [ ]]] },
      # {"dt": "Healthcare Settings"},
      {"dt": "Print Settings"},
      #{"dt": "Translation"},
      {
          "dt": "Letter Head",
          "filters": [["name", "in", [ "Template Medico", "Template Azienda"]]]
      },
      {
          "dt": "Role Profile",
          "filters": [["name", "in", [ "Utente Admin"]]]
      },
      {
          "dt": "Workspace",
          "filters": [["name", "in", ["Healthcare"]]]
        #"filters": [["name", "in", [ "Home", "Healthcare"]]]

      },
      #{"dt":"Patient History Settings"}

]

# include js in doctype views
doctype_js = {
   #"Practitioner Schedule" : "health_upgrade/overrides/practitioner_schedule/practitioner_schedule.js"
    "Practitioner Schedule" : "public/js/practitioner_schedule.js",
    "Patient Appointment": "public/js/patient_appointment.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Customer": "public/js/customer.js",
    "Company": "public/js/company.js",
    "Patient": "public/js/patient.js",
    "Patient History Settings": "public/js/patient_history_settings.js"
}
doctype_list_js = {"Sales Invoice" : "public/js/sales_invoice_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"Patient Appointment" : "public/js/patient_appointment_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": ["health_upgrade.health_upgrade.overrides.customer.get_default_address_and_contact_data"]
#	"filters": "health_upgrade.utils.jinja_filters"
}

#jenv = {
#	"methods": [
#		"get_default_address_and_contact_data:health_upgrade.health_upgrade.overrides.customer.get_default_address_and_contact_data"
#	]
#}


# Installation
# ------------

# before_install = "health_upgrade.install.before_install"
after_install = "health_upgrade.setup.setup_health_upgrade"

# Uninstallation
# ------------

before_uninstall = "health_upgrade.uninstall.before_uninstall"
# after_uninstall = "health_upgrade.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "health_upgrade.utils.before_app_install"
# after_app_install = "health_upgrade.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "health_upgrade.utils.before_app_uninstall"
# after_app_uninstall = "health_upgrade.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "health_upgrade.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Patient Appointment" : "health_upgrade.health_upgrade.overrides.patient_appointment.PatientAppointmentHC",
	"Sales Invoice": "health_upgrade.health_upgrade.overrides.sales_invoice.SalesInvoiceHC",
    "Company": "health_upgrade.health_upgrade.overrides.company.CompanyHC",
    "Patient": "health_upgrade.health_upgrade.overrides.patient.PatientHC"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_submit": "health_upgrade.health_upgrade.overrides.patient_history_settings.create_medical_record",
		"on_cancel": "health_upgrade.health_upgrade.overrides.patient_history_settings.delete_medical_record",
		"on_update_after_submit": "health_upgrade.health_upgrade.overrides.patient_history_settings.update_medical_record",
	},
    "Sales Invoice": {
		"on_submit": [
			"health_upgrade.health_upgrade.overrides.regional.utils.sales_invoice_on_submit",
		]
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"health_upgrade.tasks.all"
#	],
#	"daily": [
#		"health_upgrade.tasks.daily"
#	],
#	"hourly": [
#		"health_upgrade.tasks.hourly"
#	],
#	"weekly": [
#		"health_upgrade.tasks.weekly"
#	],
#	"monthly": [
#		"health_upgrade.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "health_upgrade.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"healthcare.healthcare.doctype.patient_appointment.patient_appointment.get_availability_data": "health_upgrade.health_upgrade.overrides.patient_appointment.get_availability_data",
    "healthcare.healthcare.doctype.patient_appointment.patient_appointment.get_events": "health_upgrade.health_upgrade.overrides.patient_appointment.get_events",
 	"frappe.desk.page.setup_wizard.setup_wizard.setup_complete": "health_upgrade.health_upgrade.overrides.setup_wizard.setup_complete",
  	"healthcare.healthcare.doctype.patient_history_settings.validate_medical_record_required": "health_upgrade.health_upgrade.overrides.patient_history_settings.validate_medical_record_required",
    "healthcare.healthcare.utils.get_healthcare_services_to_invoice": "health_upgrade.health_upgrade.utils.get_healthcare_services_to_invoice",
    "erpnext.regional.italy.utils.generate_single_invoice": "health_upgrade.health_upgrade.overrides.regional.utils.generate_single_invoice",
    "healthcare.healthcare.utils.get_appointment_billing_item_and_rate": "health_upgrade.health_upgrade.utils.get_appointment_billing_item_and_rate"
 }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Patient": "health_upgrade.health_upgrade.overrides.patient_dashboard.get_data"
 }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["health_upgrade.utils.before_request"]
# after_request = ["health_upgrade.utils.after_request"]

# Job Events
# ----------
# before_job = ["health_upgrade.utils.before_job"]
# after_job = ["health_upgrade.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"health_upgrade.auth.validate"
# ]

# Monkey patching
# ------------------
# Imports specific to the patches
#import erpnext.regional.italy.utils
#import health_upgrade.health_upgrade.overrides.sales_invoice
#erpnext.regional.italy.utils.prepare_and_attach_invoice = health_upgrade.health_upgrade.overrides.sales_invoice.prepare_and_attach_invoice
