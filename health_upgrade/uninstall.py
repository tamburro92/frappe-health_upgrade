import click
import frappe

from healthcare.setup import before_uninstall as remove_customizations

def before_uninstall():
	try:
		print("Removing customizations created by Frappe Health...")
		#do 2time: bug?
		remove_patient_history_settings()
		remove_patient_history_settings()

	except Exception as e:
		BUG_REPORT_URL = "https://github.com/frappe/health/issues/new"
		click.secho(
			"Removing Customizations for Frappe Health failed due to an error."
			" Please try again or"
			f" report the issue on {BUG_REPORT_URL} if not resolved.",
			fg="bright_red",
		)
		raise e

	click.secho("Frappe Health app customizations have been removed successfully...", fg="green")


def remove_patient_history_settings():
	patient_history_dt = ['Visita oculistica', 'Prescrizione lenti', 'Prescrizione Lenti', 'Procedura Oculistica']
	
	print("Reset Patient History Settings...")

	settings = frappe.get_single("Patient History Settings")
	for item in settings.standard_doctypes:
		if item.document_type in patient_history_dt:
			settings.standard_doctypes.remove(item)
	
	for idx, item in enumerate(settings.standard_doctypes, start=1):
		item.idx = idx
	settings.save()
