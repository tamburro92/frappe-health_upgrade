frappe.ui.form.on('Prescrizione lenti', {
	refresh: function(frm) {
		ultime_visite_bt(frm);
	},
	appointment: function(frm) {
		frm.events.set_appointment_fields(frm);
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
	}
});


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

extend_cscript(cur_frm.cscript, new health_upgrade.utils.PatientDocController({ frm: cur_frm }));
