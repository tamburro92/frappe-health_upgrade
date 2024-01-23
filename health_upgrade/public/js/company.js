frappe.ui.form.on("Company", {
    setup: function(frm){
        frm.set_query('hc_default_bollo_template', function() {
			return {filters: {'company': frm.doc.name}}});

			frm.set_query('hc_default_zero_vat_template', function() {
				return {filters: {'company': frm.doc.name}}});

    },
	onload: function(frm){
		if(frm.doc.__islocal == 1){
			frm.set_value({default_currency: "EUR"});
			frm.set_value({create_chart_of_accounts_based_on: "Standard Template"});
			frm.set_value({chart_of_accounts: "Standard"});
		}
	},
    refresh: function(frm){
	},	
});
