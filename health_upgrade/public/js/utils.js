frappe.provide("health_upgrade.utils");

//copy erpnext.utils.map_current_doc
//override get_datatable_columns
health_upgrade.utils.map_current_doc = function (opts) {
	function _map() {
		return frappe.call({
			// Sometimes we hit the limit for URL length of a GET request
			// as we send the full target_doc. Hence this is a POST request.
			type: "POST",
			method: "frappe.model.mapper.map_docs",
			args: {
				method: opts.method,
				source_names: opts.source_name,
				target_doc: cur_frm.doc,
				args: opts.args,
			},
			callback: function (r) {
				if (!r.exc) {
					frappe.model.sync(r.message);
					cur_frm.dirty();
					cur_frm.refresh();
				}
			},
		});
	}

	let query_args = {};
	if (opts.get_query_filters) {
		query_args.filters = opts.get_query_filters;
	}

	if (opts.get_query_method) {
		query_args.query = opts.get_query_method;
	}

	if (query_args.filters || query_args.query) {
		opts.get_query = () => query_args;
	}

	if (opts.source_doctype) {
		let data_fields = [];
		if (["Purchase Receipt", "Delivery Note"].includes(opts.source_doctype)) {
			data_fields.push({
				fieldname: "merge_taxes",
				fieldtype: "Check",
				label: __("Merge taxes from multiple documents"),
			});
		}
		const d = new frappe.ui.form.MultiSelectDialog({
			doctype: opts.source_doctype,
			target: opts.target,
			date_field: opts.date_field || undefined,
			setters: opts.setters,
			data_fields: data_fields,
			get_query: opts.get_query,
			add_filters_group: 1,
			allow_child_item_selection: opts.allow_child_item_selection,
			child_fieldname: opts.child_fieldname,
			child_columns: opts.child_columns,
			size: opts.size,
            columns: opts.columns,
            get_datatable_columns: function() {
                // if columns return columns
                if (this.columns) return this.columns;

                if (Array.isArray(this.setters))
                    return ["name", ...this.setters.map((df) => df.fieldname)];
        
                return ["name", ...Object.keys(this.setters)];
            },
			action: function (selections, args) {
				let values = selections;
				if (values.length === 0) {
					frappe.msgprint(__("Please select {0}", [opts.source_doctype]));
					return;
				}
				opts.source_name = values;
				if (
					opts.allow_child_item_selection ||
					["Purchase Receipt", "Delivery Note"].includes(opts.source_doctype)
				) {
					// args contains filtered child docnames
					opts.args = args;
				}
				d.dialog.hide();
				_map();
			},
		});

		return d;
	}

	if (opts.source_name) {
		opts.source_name = [opts.source_name];
		_map();
	}
};


health_upgrade.utils.PatientDocController = class PatientDocController extends frappe.ui.form.Controller {
	constructor(obj) {
		super(obj);
		this.patientInfo = {};
	}

	refresh(){
		this.storia_paziente_btn()
		this.set_patient_info();
		//this.frm.script_manager.trigger('set_patient_info');
	}
	patient(){
		this.set_patient_info(true);
		//this.frm.script_manager.trigger('set_patient_info');
	}
	set_patient_info(set_doc_fields=false){
		let frm = this.frm;
		var me = this;
		var set_doc_fields = set_doc_fields;

		var valuesCTX = {
			'patient_age': '',
			'patient_name':'',
			'patient_sex': '',
			'inpatient_record': '',
			'inpatient_status': '',
			'address': '',
			'dob': ''
		};

		if (frm.doc.patient) {
			let promisePatientDetail = frappe.call({
				method: 'healthcare.healthcare.doctype.patient.patient.get_patient_detail',
				args: {patient: frm.doc.patient}
			});
			let promisePatientAddress = frappe.call({
				method: 'health_upgrade.health_upgrade.overrides.customer.get_default_address_and_contact_data',
				args: {doctype: 'Patient',name: frm.doc.patient}
			});

			Promise.all([promisePatientDetail, promisePatientAddress]).then(([resultDetail, resultAddress]) => {
				if(resultDetail.message){
					let data = resultDetail;
					
					const age = data.message.dob ? me.calculate_age(data.message.dob) : '';
					valuesCTX.patient_age = age;
					valuesCTX.patient_name = data.message.patient_name;
					valuesCTX.patient_sex = data.message.patient_sex;
					valuesCTX.inpatient_record = data.message.inpatient_record;
					valuesCTX.inpatient_status = data.message.inpatient_status;
					valuesCTX.dob = data.message.dob;
				}
				if(resultAddress.message && resultAddress.message.address){
					let data = resultAddress;
					let address = [data.message.address.address_line1, data.message.address.city,  data.message.address.state_code, data.message.address.pincode];
					let addressFilter = address.filter(str => str !== null && str !== undefined && str !== "")
					
					valuesCTX.address = addressFilter.join(", ");
				}
				me.add_patient_info(valuesCTX, set_doc_fields);
			});
		} else {
			me.add_patient_info(valuesCTX, set_doc_fields);
		}
	}
	add_patient_info(values, set_doc_fields) {
		if(set_doc_fields)
			this.frm.set_value(values);
		// update sidebar
		const keyMap = {
			'patient_name': 'Nome Paziente',
			'patient_age': 'Età Paziente',
			'patient_sex': 'Sesso Paziente',
			'dob': 'Data di Nascita',
			'inpatient_record': 'Cartella Clinica',
			'inpatient_status': 'Stato Paziente',
			'address': 'Indirizzo'
		};
	
		let listId = 'patient-info-list';
	
		let $ul = $('<div class="' + listId + '"><ul class="list-unstyled sidebar-menu"></ul></div>');
	
		$.each(keyMap, function(key, readableKey) {
			let value = values[key];
			if (value) {
				if (key === 'dob') {
					value = moment(value).format('DD-MM-YYYY');
				}
				$ul.append('<li class="sidebar-label mb-0"><b>' + readableKey + ':</b></li>');
				$ul.append('<li class="sidebar-label">' + value + '</li>');

			}
		});
		
		if ($('.' + listId).length) {
			// Se esiste, rimuovi la lista precedente
			$('.' + listId).remove();
		}
		$ul.prependTo('.form-sidebar');
	}

	calculate_age(birth) {
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years =  age.getFullYear() - 1970;
	return `${years} ${__('Years(s)')} ${age.getMonth()} ${__('Month(s)')} ${age.getDate()} ${__('Day(s)')}`;
	}

	storia_paziente_btn() {
		var me = this;
		this.frm.add_custom_button(__('Patient History'), function() {
			frappe.route_options = { 'patient': me.frm.doc.patient };
			frappe.set_route('patient_history');
		}, __('View'));
		
	}
}


