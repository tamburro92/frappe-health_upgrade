frappe.ui.form.on('Prescrizione Lenti', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 0 ) {
			ultime_visite_bt(frm);
		}

	}
});

var ultime_visite_bt = function(frm) {
	frm.add_custom_button(__('Ultime Visite'),
		function() {
			erpnext.utils.map_current_doc({
				method: "health_upgrade.health_upgrade.doctype.prescrizione_lenti.prescrizione_lenti.make_prescrizione_lenti",
				source_doctype: "Prescrizione Lenti",
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