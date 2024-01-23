frappe.ui.form.on("Sales Invoice", {
    setup: function(frm){
        // When the user clicks Menu > EMail, the custom email_doc function will trigger the HealthommunicationComposer dialog.
        // with the doc.health_print_format set as default.
        frm.email_doc = email_doc_custom
    },
    refresh: function(frm) {
        frm.set_df_property("service_unit", "hidden", 1);
        frm.set_df_property("ref_practitioner", "hidden", 1);

    },
    on_submit(frm){
        frm.reload_doc();
    },
    hc_appointment: function(frm){
        frappe.db.get_value("Patient Appointment", frm.doc.hc_appointment, ["company","practitioner",]).then(r => {
            frm.set_value("company", r.message.company);
            frm.set_value("hc_practitioner", r.message.practitioner);

        })     
    },
    hc_mode_of_payment: function(frm){
        if(frm.doc.hc_mode_of_payment){
            // set mode of payment in the child table
            frm.clear_table("payment_schedule");
            /*
            let ps = frm.add_child("payment_schedule");
            ps.mode_of_payment = frm.doc.hc_mode_of_payment;
            ps.due_date = frm.doc.posting_date;
            */
            refresh_field("payment_schedule");
        }
    },
    company: function(frm){
        frappe.db.get_value("Company", frm.doc.company, ["hc_naming_series"]).then(r => {
            frm.set_value("naming_series", r.message.hc_naming_series);
        })
    }
});

frappe.ui.form.on("Sales Invoice Item", {
    item_code: function(frm, cdt, cdn) {
        set_tax_template(frm);
        frm.clear_table('payment_schedule')
    },
    price_list_rate: function(frm, cdt, cdn) {
        // This event is is triggered after the user selects the item_code.
        // 'rate' and 'qty' are not triggered after item_code.
        // At this point, price_list_rate can be used to calculate the item.
        set_tax_template(frm);
        frm.clear_table('payment_schedule')
    },
    qty: function(frm, cdt, cdn) {
        set_tax_template(frm);
        frm.clear_table('payment_schedule')
    },
    rate: function(frm, cdt, cdn) {
        set_tax_template(frm);
        frm.clear_table('payment_schedule')
    }
});


//By law, Bollo should not be applied if total is below 77 euros.
//Set Bollo Tax template or zero vat tax template are set
// USE "TAX RULE" for Buisness invoice!
async function set_tax_template(frm) {
	var templates = await frappe.model.get_value("Company", frm.doc.company, ["hc_default_bollo_template", "hc_default_zero_vat_template"]);
	if (!templates) {
		templates = await frappe.db.get_value("Company", frm.doc.company, ["hc_default_bollo_template", "hc_default_zero_vat_template"]);
	}

	var doc_total = 0.0
	frm.doc.items.forEach((item) => {
		if (item.rate) {
			doc_total += (item.rate * item.qty)
		} else if (item.price_list_rate) {
			doc_total += (item.price_list_rate * item.qty)
		}
	})
	if (doc_total < 77) {
        frm.set_value("taxes_and_charges", templates.message.hc_default_zero_vat_template);
	} else {
		frm.set_value("taxes_and_charges", templates.message.hc_default_bollo_template);
	}
	refresh_field("taxes_and_charges");
    frm.trigger("taxes_and_charges");
}

function email_doc_custom(message) {
    new frappe.views.CommunicationComposerExt({
        doc: this.doc,
        frm: this,
        subject: __(this.meta.name) + ": " + this.docname,
        recipients: this.doc.email || this.doc.email_id || this.doc.contact_email,
        attach_document_print: true,
        message: message,
        select_print_format: "Fattura Medico"
    });
}

frappe.views.CommunicationComposerExt = class extends frappe.views.CommunicationComposer {
    setup_print() {
		// print formats
		const fields = this.dialog.fields_dict;

		// toggle print format
		$(fields.attach_document_print.input).click(function () {
			$(fields.select_print_format.wrapper).toggle($(this).prop("checked"));
		});

		// select print format
		$(fields.select_print_format.wrapper).toggle(false);

		if (this.frm) {
			const print_formats = frappe.meta.get_print_formats(this.frm.meta.name);
			$(fields.select_print_format.input)
				.empty()
				.add_options(print_formats)
				.val(print_formats[1]);

            if (this.frm.doc && this.frm.doctype === "Sales Invoice") {
                frappe.db.get_value("Company", this.frm.doc.company, ["default_print_company","default_letter_head"])
                .then(r => {
                    if(r.message.default_print_company)
                        $(fields.select_print_format.input).val(r.message.default_print_company)
                });
            }
		} else {
			$(fields.attach_document_print.wrapper).toggle(false);
		}
	}

}

