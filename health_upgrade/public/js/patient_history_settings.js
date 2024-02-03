
frappe.ui.form.on('Patient History Settings', {
	refresh: function(frm) {
        console.log("HELLo")
		frm.set_query('document_type', 'custom_doctypes', () => {
			return {
				filters: {
				}
			};
		});
	}
})