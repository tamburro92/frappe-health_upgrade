// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Practitioner Schedule', {
	refresh: function(frm) {
		cur_frm.fields_dict["time_slots"].grid.clear_custom_buttons();
		cur_frm.fields_dict["time_slots"].grid.wrapper.find('.grid-add-row').show();

		frm.add_custom_button(__('Add Time Slots by Date'), () => {
			if(frm.is_new()){
				frappe.throw(
					__("You have unsaved changes in this form. Please save before you continue.")
				);
			}

            var d = new frappe.ui.Dialog({
				fields: [
                    {fieldname: 'from_date', label: __('From Date'), fieldtype:'Date',reqd: 1},
					{fieldname: 'cb0', fieldtype:"Column Break"},
					{fieldname: 'to_date', label: __('To Date'), fieldtype:'Date' ,reqd: 1},
					{fieldname: 'sb1', fieldtype:"Section Break"},
					{fieldname: 'monday', label: __("Monday"), fieldtype:"Check", default:1},
					{fieldname: 'tuesday', label: __("Tuesday"), fieldtype:"Check"},
					{fieldname: 'wednesday', label: __("Wednesday"), fieldtype:"Check"},
					{fieldname: 'thursday', label: __("Thursday"), fieldtype:"Check"},
					{fieldname: 'cb1', fieldtype:"Column Break"},
					{fieldname: 'friday', label: __("Friday"), fieldtype:"Check"},
					{fieldname: 'saturday', label: __("Saturday"), fieldtype:"Check"},
					{fieldname: 'sunday', label: __("Sunday"), fieldtype:"Check"},
					{fieldname: 'sb2', fieldtype:"Section Break"},
                    {fieldname: 'from_time', label: __('From Time'), fieldtype:'Time','default': '09:00:00', reqd: 1, "description": "ad esempio scrivi  11:00" },
                    {fieldname: 'to_time', label: __('To Time'), fieldtype:'Time', 'default': '12:00:00', reqd: 1, "description": "ad esempio scrivi 11:20" },
					{fieldname: 'duration', label:__('Appointment Duration (mins)'),
						fieldtype:'Int', 'default': 20, reqd: 1},
				],
				primary_action_label: __('Add Timeslots'),

                primary_action: () => {

                    var values = d.get_values();

                    if(values) {
						frappe.call({
							method: "health_upgrade.health_upgrade.overrides.practitioner_schedule.add_slots",
							args: {
                                docname: frm.doc.name,
								values: values
							},
							callback: function(r){
								if (!r.exc) {
									d.hide();
									frappe.show_alert("Slots Added");
		
									frappe.run_serially([
										() => frm.reload_doc(),
										() => frm.save()]);
								}else{
									frappe.show_alert(err);
								}
							}
						})
					}
				}
			});
			d.show();
		});

		frm.add_custom_button(__("Delete all Slots"), function(){
			frappe.confirm(__('Delete all slots?'),
			    function(){
					/*
					frm.clear_table("time_slots");
					frm.refresh_fields();
					*/
					frappe.call({
						method: "health_upgrade.health_upgrade.overrides.practitioner_schedule.delete_all_slots",
						args: {
							docname: frm.doc.name
						}, 
						callback: function(r){
							if (!r.exc) {
								frm.clear_table("time_slots");
								refresh_field("time_slots");
							} 
							else{
								frappe.msgprint({
									message:__(`Cannot delete some of the rows because HC Practitioner Schedule ${frm.doc.name} is linked with HC Patient Appointments.`), 
									title:__('Message'), indicator:'red', alert: true})
							}
						}
					})
					
			    });
		});
	}
})
		
	

