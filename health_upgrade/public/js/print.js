/*
frappe.pages["print"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
	});

	let print_view = new frappe.ui.form.PrintViewExt(wrapper);

	$(wrapper).bind("show", () => {
		const route = frappe.get_route();
		const doctype = route[1];
		const docname = route.slice(2).join("/");
		if (!frappe.route_options || !frappe.route_options.frm) {
			frappe.model.with_doc(doctype, docname, () => {
				let frm = { doctype: doctype, docname: docname };
				frm.doc = frappe.get_doc(doctype, docname);
				frappe.model.with_doctype(doctype, () => {
					frm.meta = frappe.get_meta(route[1]);
					print_view.show(frm);
				});
			});
		} else {
			print_view.frm = frappe.route_options.frm.doctype
				? frappe.route_options.frm
				: frappe.route_options.frm.frm;
			frappe.route_options.frm = null;
			print_view.show(print_view.frm);
		}
	});
};

frappe.ui.form.PrintViewExt = class extends frappe.ui.form.PrintView {

    set_print_format(){
        if (this.frm.doc && this.frm.doctype === "Sales Invoice") {
            frappe.db.get_value("Company", this.frm.doc.company, ["default_print_company","default_letter_head"])
            .then(r => {
                if(r.message.default_print_company)
                    this.print_sel.val(r.message.default_print_company)
                if(r.message.default_letter_head)
                    this.letterhead_selector.val(r.message.default_letter_head)
                this.preview()
                
            });
        }
    }

    show(frm){
        this.frm = frm;
        this.set_title();
        this.set_breadcrumbs();
        this.setup_customize_dialog();
    
        let tasks = [
            this.refresh_print_options,
            this.set_default_print_language,
            this.set_letterhead_options,
            this.set_print_format
            //this.preview,
        ].map((fn) => fn.bind(this));
    
        this.setup_additional_settings();
        return frappe.run_serially(tasks);
    }
}
*/