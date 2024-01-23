
frappe.ui.form.on("Patient Appointment", {
	onload: function(frm) {
		//frm.set_df_property("appointment_type","reqd",0);
		//frm.set_df_property("appointment_type","hidden",1)

		check_patient_details(frm);	
	},
    refresh: function(frm){
		frm.remove_custom_button('Invoice', 'Create');
		if(frm.doc.__islocal == 1)
            return

		if (!frm.doc.ref_sales_invoice) {
				frappe.db.get_single_value("HC Settings", "check_patient_billing_in_appointment").then((value) => {
					if (value===1) {
						frm.add_custom_button(__("Generate Invoice"), function() {
							generate_invoice(frm);
						});
					}
			});
		}

		if (frm.doc.ref_sales_invoice) {
			frm.add_custom_button(__("Delete Linked Invoice"), function() {
				frappe.call({
					method: "health_upgrade.health_upgrade.overrides.patient_appointment.unlink_and_delete_sales_invoice",
					args: {
						appointment_id: frm.doc.name
					},
					freeze: true,
					freeze_message: __("Deleting linked invoice...")
				}).done(function(r) {
					frappe.msgprint({
						title: __("Invoice Message"),
						indicator: "green",
						message: __("Invoice deleted successfully")
					});
					frm.reload_doc();
				}).error(function(r) {
					frappe.show_alert(__("Cannot unlink sales invoice"));
				});
			});
		}

		if (["Open", "Checked In"].includes(frm.doc.status) || (frm.doc.status == 'Scheduled' && !frm.doc.__islocal)) {
				frm.add_custom_button(__('Clinical Procedure'), function() {
					frappe.model.open_mapped_doc({
						method: 'healthcare.healthcare.doctype.clinical_procedure.clinical_procedure.make_procedure',
						frm: frm,
					});
				}, __('Create'));
		}

		check_patient_details(frm)
    },

	practitioner: function(frm) {
		if (!frm.doc.practitioner) { return 0; }
		frappe.call({
			method: "health_upgrade.health_upgrade.overrides.patient_appointment.get_earliest_available_date",
			args: {
				"practitioner": frm.doc.practitioner,
				//"procedure_room": frm.doc.procedure_room
			},
			callback: (r) => {
				if (r.message) {
					frm.set_value("appointment_date", r.message);
				}
			}
		});

		/*
		if(frm.doc.practitioner){
			frappe.db.get_value('Healthcare Practitioner', frm.doc.healthcare_practitioner, 'hc_appointment_color', function(response){
				frm.set_value("appointment_color", response.hc_appointment_color);
			});
		}
		*/
	},
	hc_procedure: function(frm) {
		//if (!frm.doc.patient) { return 0; }

		if(frm.doc.hc_procedure){
			frappe.db.get_value("Item", frm.doc.hc_procedure, ["hc_procedure_room", "item_name", "hc_requires_nurse", "hc_requires_anaesthetist"], function(r) {
				if (r.hc_procedure_room) frm.set_value("hc_procedure_room", r.hc_procedure_room); 
				if (r.item_name) frm.set_value("hc_procedure_name", r.item_name);
				if (r.hc_requires_nurse) frm.set_value("hc_requires_nurse", r.hc_requires_nurse); 
				if (r.hc_requires_anaesthetist) frm.set_value("requires_anaesthetist", r.hc_requires_anaesthetist); 

				frm.set_value("appointment_for","Practitioner");

			})
		} else {
			// Clear physician and appointment_date if this field has no value
			frm.set_value("practitioner", undefined);
			frm.set_value("appointment_date", undefined);
			return
		}
	},
	
	// used to assign company and naming series to health_upgrade
    practitioner: function(frm){
        if(frm.doc.practitioner){
            frappe.db.get_value("Healthcare Practitioner", frm.doc.practitioner, ["hc_company"], function(r) {
                if (r.hc_company){
                    frm.set_value("company", r.hc_company); 
                }
            })        
        }
    },
	
    after_save: function(frm) {
		frm.set_df_property('company', 'read_only', 1)
	},
	
    hc_check_date: function(frm){
		if (frm.doc.__islocal) {
			check_patient_availability(frm);
        }    
    }
	
});

var generate_invoice = function(frm){
	var doc = frm.doc;

	frappe.call({
		method:	"health_upgrade.health_upgrade.overrides.patient_appointment.create_invoice",
		args: {
			company: doc.company,
			practitioner:doc.practitioner, 
			patient: doc.patient,
			appointment_id: doc.name, 
			appointment_date:doc.appointment_date
		},
		callback: function(data){
			if(!data.exc){
					//frappe.set_route("Form", "Sales Invoice", data.message);
                    //set_status(frm);
					frm.reload_doc();
			}
		}
	});
};

function check_patient_availability(frm) {
	
	let physician = frm.doc.practitioner;
	let appointment_date = frm.doc.appointment_date || frappe.datetime.get_today();

	if(!(physician)) {
		frappe.throw(__("Please select Practitioner"));
	}

	// show booking modal

	frappe.call({
        method: "health_upgrade.health_upgrade.overrides.patient_appointment.get_availability_dates",
		args: {
			date: appointment_date,
			practitioner: physician,
			appointment : frm.doc
		},
		callback: (r) => {
			var data = r.message;
			//if(r.message.availability_data && data.availability_data.length > 0) {
			//	show_availability(data);
			// } else {
				show_empty_state(frm, data);
			// }
		}
	});

    function show_empty_state(frm, data) {
	
		let available_date_html = data.availability_data.map(av_date => {
			return `<a data-name=${av_date.original}>${av_date.formatted}</a>`;
		}).join("<br/>");


		let empty_state_dialog = new frappe.ui.Dialog({
			title: __('Practitioner Available Dates'),
			fields: [
				{
					"fieldtype": "HTML",
					"fieldname": "message"
				}
			]
		})
		let $empty_state_dialog_wrapper = empty_state_dialog.fields_dict.message.$wrapper;
		let empty_state_msg;

		if(!available_date_html){
			empty_state_msg = __("Practitioner {0} is currently unavailable. ", [data.physician.bold()])
		} else{
			empty_state_msg = __("{0} is available on the following dates: <br><hr/> {1}", [
				data.physician.bold(),
				available_date_html
			])
		}

		$empty_state_dialog_wrapper
			.css({'margin-bottom': 0,'overflow': 'auto', 'max-height': '200px'})
			.html(empty_state_msg);

		$empty_state_dialog_wrapper.on('click', 'a', function() {
			var $date_btn = $(this);
			frm.set_value("appointment_date", $date_btn.attr('data-name'))
			empty_state_dialog.hide();
		});
		empty_state_dialog.show();
	}
};


function check_patient_details(frm) {
	if (frm.doc.patient){
		frappe.db.get_single_value("HC Settings", "check_patient_billing_in_appointment").then((value) => {
			if (value===1) {
				frappe.call({
					method: "health_upgrade.health_upgrade.overrides.patient_appointment.check_patient_details",
					args: {
						patient: frm.doc.patient,
					},
					callback: (r) => {
						if (r && r.message && r.message.missing_details && r.message.missing_details.length > 0) {
							let url = "/app/customer/" + r.message.patient_customer
							if (frappe.boot.versions.erpnext.indexOf('12') != -1) {
								url = "desk#Form/Customer/" + r.message.patient_customer
							}
			
							frm.set_df_property("patient", "label",
								__("Patient") + '<a class="badge" style="color:white;background-color:red;margin:10px;padding:4px" href="' + url + '">'
								+ __("Mancano le informazioni cliente!") + '</a>'
								+ '<p style="color:red">('+ r.message.missing_details +')</p>'
							);
						} else {
							frm.set_df_property("patient", "label", __("Patient"));
						}
					}
				});
			}
		});
	}

	
}


// override function check_and_set_availability
check_and_set_availability = function(frm) {
	
	let selected_slot = null;
	let service_unit = null;
	let duration = null;
	let add_video_conferencing = null;
	let overlap_appointments = null;
	let appointment_based_on_check_in = false;

	show_availability();

	function show_empty_state(practitioner, appointment_date) {
		frappe.msgprint({
			title: __('Not Available'),
			message: __('Healthcare Practitioner {0} not available on {1}', [practitioner.bold(), appointment_date.bold()]),
			indicator: 'red'
		});
	}

	function show_availability() {
		let selected_practitioner = '';
		let d = new frappe.ui.Dialog({
			title: __('Available slots'),
			fields: [
				{ fieldtype: 'Link', options: 'Healthcare Practitioner', reqd: 1, fieldname: 'practitioner', label: 'Healthcare Practitioner' },
				{ fieldtype: 'Column Break' },
				{ fieldtype: 'Date', reqd: 1, fieldname: 'appointment_date', label: 'Date', min_date: new Date(frappe.datetime.get_today()) },
				{ fieldtype: 'Section Break' },
				{ fieldtype: 'HTML', fieldname: 'available_slots' },
			],
			primary_action_label: __('Prenota'),
			primary_action: async function() {
				frm.set_value('appointment_time', selected_slot);
				add_video_conferencing = add_video_conferencing && !d.$wrapper.find(".opt-out-check").is(":checked")
					&& !overlap_appointments

				frm.set_value('add_video_conferencing', add_video_conferencing);
				if (!frm.doc.duration) {
					frm.set_value('duration', duration);
				}
				let practitioner = frm.doc.practitioner;

				frm.set_value('practitioner', d.get_value('practitioner'));
				frm.set_value('appointment_date', d.get_value('appointment_date'));
				frm.set_value('appointment_based_on_check_in', appointment_based_on_check_in)

				if (service_unit) {
					frm.set_value('service_unit', service_unit);
				}

				d.hide();
				frm.enable_save();
				await frm.save();
				if (!frm.is_new() && (!practitioner || practitioner == d.get_value('practitioner'))) {
					await frappe.db.get_single_value("Healthcare Settings", "show_payment_popup").then(val => {
						frappe.call({
							method: "healthcare.healthcare.doctype.fee_validity.fee_validity.check_fee_validity",
							args: { "appointment": frm.doc },
							callback: (r) => {
								if (val && !r.message && !frm.doc.invoiced) {
									make_payment(frm, val);
								} else {
									frappe.call({
										method: "healthcare.healthcare.doctype.patient_appointment.patient_appointment.update_fee_validity",
										args: { "appointment": frm.doc }
									});
								}
							}
						});
					});
				}
				d.get_primary_btn().attr('disabled', true);
			}
		});

		d.set_values({
			'practitioner': frm.doc.practitioner,
			'appointment_date': frm.doc.appointment_date,
		});

		// disable dialog action initially
		d.get_primary_btn().attr('disabled', true);

		// Field Change Handler

		let fd = d.fields_dict;

		d.fields_dict['appointment_date'].df.onchange = () => {
			show_slots(d, fd);
		};
		d.fields_dict['practitioner'].df.onchange = () => {
			if (d.get_value('practitioner') && d.get_value('practitioner') != selected_practitioner) {
				selected_practitioner = d.get_value('practitioner');
				show_slots(d, fd);
			}
		};

		d.show();
	}
	function show_slots(d, fd) {
		if (d.get_value('appointment_date') && d.get_value('practitioner')) {
			fd.available_slots.html('');
			frappe.call({
				method: 'healthcare.healthcare.doctype.patient_appointment.patient_appointment.get_availability_data',
				args: {
					practitioner: d.get_value('practitioner'),
					date: d.get_value('appointment_date'),
					appointment: frm.doc
				},
				callback: (r) => {
					let data = r.message;
					if (data.slot_details.length > 0) {
						let $wrapper = d.fields_dict.available_slots.$wrapper;

						// make buttons for each slot
						let slot_html = get_slots(data.slot_details, data.fee_validity, d.get_value('appointment_date'));

						$wrapper
							.css('margin-bottom', 0)
							.addClass('text-center')
							.html(slot_html);

						// highlight button when clicked
						$wrapper.on('click', 'button', function() {
							let $btn = $(this);
							$wrapper.find('button').removeClass('btn-outline-primary');
							$btn.addClass('btn-outline-primary');
							selected_slot = $btn.attr('data-name');
							service_unit = $btn.attr('data-service-unit');
							appointment_based_on_check_in = $btn.attr('data-day-appointment');
							duration = $btn.attr('data-duration');
							add_video_conferencing = parseInt($btn.attr('data-tele-conf'));
							overlap_appointments = parseInt($btn.attr('data-overlap-appointments'));
							// show option to opt out of tele conferencing
							if ($btn.attr('data-tele-conf') == 1) {
								if (d.$wrapper.find(".opt-out-conf-div").length) {
									d.$wrapper.find(".opt-out-conf-div").show();
								} else {
									overlap_appointments ?
										d.footer.prepend(
											`<div class="opt-out-conf-div ellipsis text-muted" style="vertical-align:text-bottom;">
												<label>
													<span class="label-area">
													${__("Video Conferencing disabled for group consultations")}
													</span>
												</label>
											</div>`
										)
									:
										d.footer.prepend(
											`<div class="opt-out-conf-div ellipsis" style="vertical-align:text-bottom;">
											<label>
												<input type="checkbox" class="opt-out-check"/>
												<span class="label-area">
												${__("Do not add Video Conferencing")}
												</span>
											</label>
										</div>`
										);
								}
							} else {
								d.$wrapper.find(".opt-out-conf-div").hide();
							}

							// enable primary action 'Book'
							d.get_primary_btn().attr('disabled', null);
						});

					} else {
						//	fd.available_slots.html('Please select a valid date.'.bold())
						show_empty_state(d.get_value('practitioner'), d.get_value('appointment_date'));
					}
				},
				freeze: true,
				freeze_message: __('Fetching Schedule...')
			});
		} else {
			fd.available_slots.html(__('Appointment date and Healthcare Practitioner are Mandatory').bold());
		}
	}
	// override function
	function get_slots(slot_details, fee_validity, appointment_date) {
		let slot_html = '';
		let appointment_count = 0;
		let disabled = false;
		let start_str, slot_start_time, slot_end_time, interval, count, count_class, tool_tip, available_slots;

		slot_details.forEach((slot_info) => {
			slot_html += `<div class="slot-info">`;
			if (fee_validity && fee_validity != 'Disabled') {
				slot_html += `
					<span style="color:green">
					${__('Patient has fee validity till')} <b>${moment(fee_validity.valid_till).format('DD-MM-YYYY')}</b>
					</span><br>`;
			} else if (fee_validity != 'Disabled') {
				slot_html += `
					<span style="color:red">
					${__('Patient has no fee validity')}
					</span><br>`;
			}


				slot_html += '</div><br>';

				slot_html += slot_info.avail_slot.map(slot => {
						appointment_count = 0;
						disabled = false;
						count_class = tool_tip = '';
						start_str = slot.from_time;
						slot_start_time = moment(slot.from_time, 'HH:mm:ss');
						slot_end_time = moment(slot.to_time, 'HH:mm:ss');
						interval = (slot_end_time - slot_start_time) / 60000 | 0;

						// restrict past slots based on the current time.
						let now = moment();
						let booked_moment = ""
						if((now.format("YYYY-MM-DD") == appointment_date) && (slot_start_time.isBefore(now) && !slot.maximum_appointments)){
							disabled = true;
						} else {
							// iterate in all booked appointments, update the start time and duration
							slot_info.appointments.forEach((booked) => {
								booked_moment = moment(booked.appointment_time, 'HH:mm:ss');
								let end_time = booked_moment.clone().add(booked.duration, 'minutes');

								// to get apointment count for all day appointments
								if (slot.maximum_appointments) {
									if (booked.appointment_date == appointment_date) {
										appointment_count++;
									}
								}
								// Deal with 0 duration appointments
								if (booked_moment.isSame(slot_start_time) || booked_moment.isBetween(slot_start_time, slot_end_time)) {
									if (booked.duration == 0) {
										disabled = true;
										return false;
									}
								}

								// Check for overlaps considering appointment duration
								if (slot_info.allow_overlap != 1) {
									if (slot_start_time.isBefore(end_time) && slot_end_time.isAfter(booked_moment)) {
										// There is an overlap
										disabled = true;
										return false;
									}
								} else {
									if (slot_start_time.isBefore(end_time) && slot_end_time.isAfter(booked_moment)) {
										appointment_count++;
									}
									if (appointment_count >= slot_info.service_unit_capacity) {
										// There is an overlap
										disabled = true;
										return false;
									}
								}
							});
						}
						if (slot_info.allow_overlap == 1 && slot_info.service_unit_capacity > 1) {
							available_slots = slot_info.service_unit_capacity - appointment_count;
							count = `${(available_slots > 0 ? available_slots : __('Full'))}`;
							count_class = `${(available_slots > 0 ? 'badge-success' : 'badge-danger')}`;
							tool_tip =`${available_slots} ${__('slots available for booking')}`;
						}

						if (slot.maximum_appointments) {
							if (appointment_count >= slot.maximum_appointments) {
								disabled = true;
							}
							else {
								disabled = false;
							}
							available_slots = slot.maximum_appointments - appointment_count;
							count = `${(available_slots > 0 ? available_slots : __('Full'))}`;
							count_class = `${(available_slots > 0 ? 'badge-success' : 'badge-danger')}`;
							return `<button class="btn btn-secondary" data-name=${start_str}
								data-service-unit="${slot_info.service_unit || ''}"
								data-day-appointment=${1}
								data-duration=${slot.duration}
								${disabled ? 'disabled="disabled"' : ""}>${slot.from_time} -
								${slot.to_time} ${slot.maximum_appointments ?
								`<br><span class='badge ${count_class}'>${count} </span>` : ''}</button>`
						} else {

						return `
							<button class="btn btn-secondary" data-name=${start_str}
								data-duration=${interval}
								data-service-unit="${slot_info.service_unit || ''}"
								data-tele-conf="${slot_info.tele_conf || 0}"
								data-overlap-appointments="${slot_info.service_unit_capacity || 0}"
								style="margin: 0 10px 10px 0; width: auto;" ${disabled ? 'disabled="disabled"' : ""}
								data-toggle="tooltip" title="${tool_tip || ''}">
								${start_str.substring(0, start_str.length - 3)}
								${slot_info.service_unit_capacity ? `<br><span class='badge ${count_class}'> ${count} </span>` : ''}
							</button>`;

				}
			}).join("");

				if (slot_info.service_unit_capacity) {
					slot_html += `<br/><small>${__('Each slot indicates the capacity currently available for booking')}</small>`;
				}
				slot_html += `<br/><br/>`;

		});

		return slot_html;
	}
};
