frappe.listview_settings['Sales Invoice'] ={
    onload: function(listview) {

    listview.page.add_menu_item(__("Download ZIP"), function() {
        
        const dialog = new frappe.ui.Dialog({
            title: __("Select Company & Month"),
            fields: [
                {
                    fieldname: "company",
                    fieldtype: "Link",
                    options: "Company",
                    label: "Company",
                    reqd: 1
                },
                {
                    fieldname: "date",
                    fieldtype: "DateRange",
                    
                    label: "Date Range",
                    reqd: 1
                }
            ],
            primary_action: function(){
                frappe.call({
                    method: 'health_upgrade.health_upgrade.overrides.sales_invoice.download_sales_invoices',
                    freeze: true,
                    args: {
                        args : this.get_values()
                    },
                    callback: function() {
                    }
                });                
                this.hide();
            },
            primary_action_label: __("Create ZIP")
        })
        dialog.show()

    });

    },

}

//# sourceURL=sales_invoice__list_js