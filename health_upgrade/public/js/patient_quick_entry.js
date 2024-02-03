frappe.provide('frappe.ui.form');
//REMEMBDER TO BUILD
// bench build --apps health_upgrade
frappe.ui.form.PatientQuickEntryForm = class PatientQuickEntryForm extends frappe.ui.form.QuickEntryForm {

	constructor(doctype, after_insert, init_callback, doc, force) {
		super(doctype, after_insert, init_callback, doc, force);
		this.skip_redirect_on_error = true;
	}

	render_dialog() {

		this.mandatory = this.get_standard_fields();

		// preserve standard_fields order, splice custom fields after Patient name fields
		//this.mandatory.splice(3, 0, ...custom_fields);

		super.render_dialog();
	}

	get_standard_fields() {
		return [
			{
				label: __('First Name'),
				fieldname: 'first_name',
				fieldtype: 'Data'
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('last Name'),
				fieldname: 'last_name',
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldtype: 'Section Break',
				collapsible: 0
			},
			{
				label: __('Gender'),
				fieldname: 'sex',
				fieldtype: 'Link',
				options: 'Gender'
			},
			{
				label: __('Codice Fiscale'),
				fieldname: 'fiscal_code',
				fieldtype: 'Data'
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('Birth Date'),
				fieldname: 'dob',
				fieldtype: 'Date'
			},
			{
				label: __('Birth Place'),
				fieldname: 'birth_place',
				fieldtype: 'Data'
			},
			{
				fieldtype: 'Section Break',
				label: __('Primary Contact'),
				collapsible: 0
			},
			{
				label: __('Email Id'),
				fieldname: 'email',
				fieldtype: 'Data',
				options: 'Email'
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('Mobile Number'),
				fieldname: 'mobile',
				fieldtype: 'Data',
				options: 'Phone'
			},
			{
				fieldtype: 'Section Break',
				label: __('Primary Address'),
				collapsible: 0
			},
			{
				label: __('Address Line 1'),
				fieldname: 'address_line1',
				fieldtype: 'Data'
			},
			{
				label: __('ZIP Code'),
				fieldname: 'pincode',
				fieldtype: 'Data'
			},
			{
				fieldtype: 'Column Break'
			},
			{
				label: __('City'),
				fieldname: 'city',
				fieldtype: 'Data'
			},
			{
				label: __('Provincia'),
				fieldname: 'state',
				fieldtype: 'Data'
			},
			{
				label: __('Sigla Provincia'),
				fieldname: 'state_code',
				fieldtype: 'Data'
			},
			{
				label: __('Country'),
				fieldname: 'country',
				fieldtype: 'Link',
				options: 'Country',
				default: 'Italy'
			}
		];
	}
}