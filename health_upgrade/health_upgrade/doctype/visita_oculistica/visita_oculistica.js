// Copyright (c) 2024, Tamburro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visita oculistica', {
	setup: function(frm) {
		style_components(frm)
	},
	refresh: function(frm) {
		if (frm.doc.docstatus === 0 ) {
			ultime_visite_bt(frm);
		}
	},
	appointment: function(frm) {
		frm.events.set_appointment_fields(frm);
	},

	patient: function(frm) {
		frm.events.set_patient_info(frm);
	},

	practitioner: function(frm) {
		if (!frm.doc.practitioner) {
			frm.set_value('practitioner_name', '');
		}
	},
	set_appointment_fields: function(frm) {
		if (frm.doc.appointment) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Patient Appointment',
					name: frm.doc.appointment
				},
				callback: function(data) {
					let values = {
						'patient':data.message.patient,
						'type': data.message.appointment_type,
						'practitioner': data.message.practitioner,
						'invoiced': data.message.invoiced,
						'company': data.message.company
					};
					frm.set_value(values);
					frm.set_df_property('patient', 'read_only', 1);
				}
			});
		}
		else {
			let values = {
				'patient': '',
				'patient_name': '',
				'type': '',
				'practitioner': '',
				'invoiced': 0,
				'patient_sex': '',
				'patient_age': '',
				'inpatient_record': '',
				'inpatient_status': ''
			};
			frm.set_value(values);
			frm.set_df_property('patient', 'read_only', 0);
		}
	},

	set_patient_info: function(frm) {
		if (frm.doc.patient) {
			frappe.call({
				method: 'healthcare.healthcare.doctype.patient.patient.get_patient_detail',
				args: {
					patient: frm.doc.patient
				},
				callback: function(data) {
					let age = '';
					if (data.message.dob) {
						age = calculate_age(data.message.dob);
					}
					let values = {
						'patient_age': age,
						'patient_name':data.message.patient_name,
						'patient_sex': data.message.sex,
						'inpatient_record': data.message.inpatient_record,
						'inpatient_status': data.message.inpatient_status
					};
					frm.set_value(values);

					if(data.message.customer){
						frappe.call({
							method: 'health_upgrade.health_upgrade.overrides.customer.get_default_address_and_contact_data',
							args: {
								doctype: 'Customer',
								name: data.message.customer
							},
							callback: function(data) {
								if(data.message.address){
									let address = (data.message.address.address_line1 + ' '|| '') + (data.message.address.pincode + ' ' || '') + (data.message.address.city + ' '|| '') +  (data.message.address.state_code || '')
									frm.set_value('address', address)
								}
							}
						});
					}
				}
			});
		} else {
			let values = {
				'patient_age': '',
				'patient_name':'',
				'patient_sex': '',
				'inpatient_record': '',
				'inpatient_status': ''
			};
			frm.set_value(values);
		}
	}
});

let calculate_age = function(birth) {
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years =  age.getFullYear() - 1970;
	return `${years} ${__('Years(s)')} ${age.getMonth()} ${__('Month(s)')} ${age.getDate()} ${__('Day(s)')}`;
};

var ultime_visite_bt = function(frm) {
	frm.add_custom_button(__('Ultime Visite'),
		function() {
			erpnext.utils.map_current_doc({
				method: "health_upgrade.health_upgrade.doctype.visita_oculistica.visita_oculistica.make_visita_oculistica",
				source_doctype: "Visita oculistica",
				target: frm,
				setters: {
					patient: frm.doc.patient || undefined,
					encounter_date: undefined
				},
				get_query_filters: {
					docstatus: 1,
					patient: frm.doc.patient
				},
				date_field: "encounter_date",
				columns: ["name", "patient", "encounter_date"],
			})
		}, __("Get Items From"));
}

var style_components = function(frm){

	// wrap a card around FOO
	let divFoo = $('div[data-fieldname="foo"]').parent()
	divFoo.wrap("<div class='card'><div class='card-body'></div></div>" );

	// dispose to column sx,dx flag
	let dxsxFoo = $('div[data-fieldname="sx_foo"]').add($('div[data-fieldname="dx_foo"]'))
	dxsxFoo.wrapAll('<div class="row"></div>')

	let sxFoo = $('div[data-fieldname="sx_foo"]')
	let dxFoo = $('div[data-fieldname="dx_foo"]')
	dxFoo.wrap('<div class="col-sm-4"> </div>')
	sxFoo.wrap('<div class="col-sm-4"> </div>')









}
/*
var get_healthcare_services_to_invoice = function(frm) {
	var me = this;
	let selected_patient = '';
	var dialog = new frappe.ui.Dialog({
		title: __("Get Items from Healthcare Services"),
		fields:[
			{
				fieldtype: 'Link',
				options: 'Patient',
				label: 'Patient',
				fieldname: "patient",
				reqd: true
			},
			{ fieldtype: 'Section Break'	},
			{ fieldtype: 'HTML', fieldname: 'results_area' }
		]
	});
	var $wrapper;
	var $results;
	var $placeholder;
	dialog.set_values({
		'patient': frm.doc.patient
	});
	dialog.fields_dict["patient"].df.onchange = () => {
		var patient = dialog.fields_dict.patient.input.value;
		if(patient && patient!=selected_patient){
			selected_patient = patient;
			var method = "";
			var args = {doctype: "Visita oculistica", filters : {patient: patient, docstatus: 1}, filters_field: ["patient", "encounter_date"], txt:""};
			var columns = (["service", "reference_name", "reference_type"]);
			perform_search(frm, true, $results, $placeholder, method, args, columns);
		}
		else if(!patient){
			selected_patient = '';
			$results.empty();
			$results.append($placeholder);
		}
	}
	$wrapper = dialog.fields_dict.results_area.$wrapper.append(`<div class="results"
		style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
	$results = $wrapper.find('.results');
	$placeholder = $(`<div class="multiselect-empty-state">
				<span class="text-center" style="margin-top: -40px;">
					<i class="fa fa-2x fa-heartbeat text-extra-muted"></i>
					<p class="text-extra-muted">No billable Healthcare Services found</p>
				</span>
			</div>`);
	$results.on('click', '.list-item--head :checkbox', (e) => {
		$results.find('.list-item-container .list-row-check')
			.prop("checked", ($(e.target).is(':checked')));
	});
	set_primary_action(frm, dialog, $results, true);
	dialog.show();
};

var perform_search = function(frm, invoice_healthcare_services, $results, $placeholder, method, args, columns) {
	$results.empty();
	frappe.call({
		type: "GET",
		method: "frappe.desk.search.search_widget",
		no_spinner: true,
		args: args,
		callback: function(res) {
			if(res.values){
				const more = res.values.length && res.values.length > this.page_length ? 1 : 0;

				$results.append(make_list_row(columns, invoice_healthcare_services));
				for(let i=0; i<res.values.length; i++){
					$results.append(make_list_row(columns, invoice_healthcare_services, res.values[i]));
				}
			}else {
				$results.append($placeholder);
			}
		}
	});

}

var set_primary_action= function(frm, dialog, $results, invoice_healthcare_services) {
	var me = this;
	dialog.set_primary_action(__('Add'), function() {
		frm.clear_table('items');
		let checked_values = get_checked_values($results);
		if(checked_values.length > 0){
			if(invoice_healthcare_services) {
				frm.set_value("patient", dialog.fields_dict.patient.input.value);
			}
			add_to_item_line(frm, checked_values, invoice_healthcare_services);
			dialog.hide();
		}
		else{
			if(invoice_healthcare_services){
				frappe.msgprint(__("Please select Healthcare Service"));
			}
			else{
				frappe.msgprint(__("Please select Drug"));
			}
		}
	});
};
*/
