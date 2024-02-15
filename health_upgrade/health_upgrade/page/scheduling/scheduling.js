frappe.pages['scheduling'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'None',
		single_column: true
	});

	page.set_title("Title");

	let field = page.add_field({
		label: 'Status',
		fieldtype: 'Select',
		fieldname: 'status',
		options: [
			'Open',
			'Closed',
			'Cancelled'
		],
		change() {
			frappe.msgprint(field.get_value());
		}
	});

	$(frappe.render_template('head',{ data:'Hello'})).appendTo(page.body);
	$(frappe.render_template('table',{ data:'Hello'})).appendTo(page.body);

}