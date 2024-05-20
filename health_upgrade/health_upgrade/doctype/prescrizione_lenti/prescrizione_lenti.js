frappe.ui.form.on('Prescrizione lenti', {
	refresh: function(frm) {
		ultime_visite_bt(frm);

		// update patient info
		if(frm.doc.__islocal){
			frm.trigger('set_patient_info');
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
	if (!frm.doc.__islocal)
		return;

	frm.add_custom_button(__('Ultime Visite'),
		function() {
			health_upgrade.utils.map_current_doc({
				method: "health_upgrade.health_upgrade.doctype.prescrizione_lenti.prescrizione_lenti.make_prescrizione_lenti",
				source_doctype: "Prescrizione lenti",
				target: frm,
				setters: {
					patient: frm.doc.patient || undefined,
					encounter_date: undefined
				},
				get_query_filters: {
					patient: frm.doc.patient
				},
				date_field: "encounter_date",
				columns: ["name", "patient", "encounter_date"],
				size: 'large'
			})
		}, __("Get Items From"));
}