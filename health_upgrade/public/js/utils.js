//copy erpnext.utils.map_current_doc
//override get_datatable_columns
frappe.provide("health_upgrade.utils");

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
