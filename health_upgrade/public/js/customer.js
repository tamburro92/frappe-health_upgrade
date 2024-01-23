frappe.ui.form.on("Customer", {
	setup: function(frm){

	},
	onload: function(frm){
		const hide_fields = ["lead_name", "opportunity_name", "account_manager", "custom_phone"];
		for (const h_field of hide_fields){
			frm.set_df_property(h_field,"hidden",1);
			//frm.fields_dict[h_field].df.hidden = 1;
		}
		
		if(frm.doc.__islocal == 1){
			frm.set_value({
				customer_group: "Tutti i gruppi di clienti",
				customer_type: "Individual",
				territory: "Italy",
				customer_type: "Individual"
			});
		}
		//frm.fields_dict.defaults_tab.df.collapsible = 1;
		//frm.fields_dict.defaults_tab.collapse(1);
		//frm.fields_dict.defaults_tab.df.collapsible_depends_on = "customer_details";
	},
    refresh: function(frm){
		frm.set_value('custom_piva',frm.doc.tax_id, undefined, true);
		frm.set_value('custom_codice_fiscale',frm.doc.fiscal_code, undefined, true);
		display_default_address_and_contact(frm);
    },
	
	// handler tax
	custom_piva: function(frm){
		if (frm.doc.custom_piva) frm.set_value('tax_id',frm.doc.custom_piva);
	},
	custom_codice_fiscale: function(frm){
		if (frm.doc.custom_codice_fiscale) frm.set_value('fiscal_code',frm.doc.custom_codice_fiscale);
	},
	first_name: function(frm){ 
		frm.set_value('customer_name',(frm.doc.last_name||"") + " "+ (frm.doc.first_name||""));
	},
	last_name: function(frm){
		frm.set_value('customer_name',(frm.doc.last_name||"") + " "+ (frm.doc.first_name||""));

	},
	custom_modifica_indirizzo: function(frm) {
		if(frm.doc.__islocal == 1){
			frappe.msgprint(__('Salva prima il documento'));
			return
		}
            
		var d = show_address_dialog(frm);
		d.show();
	},
});


var display_default_address_and_contact = function(frm){
	frappe.call({
		method: "health_upgrade.health_upgrade.overrides.customer.get_default_address_and_contact_data",
		args: {
			doctype: "Customer",
			name: frm.doc.name
		},
		callback: function(r){
			if(r.message){
				if(r.message.address){					
					frm.set_value( "custom_address_line_1", r.message.address.address_line1, undefined, true);
					frm.set_value( "custom_address_line_2", r.message.address.address_line2, undefined, true);
					frm.set_value( "custom_pincode", r.message.address.pincode, undefined, true);
					frm.set_value( "custom_address_town", r.message.address.city, undefined, true);
					frm.set_value( "custom_country", r.message.address.country, undefined, true);			
				}
				if(r.message.contact){
					frm.set_value( "custom_email", r.message.contact.email_id, undefined, true);
					frm.set_value( "custom_phone", r.message.contact.phone, undefined, true);
					frm.set_value( "custom_mobile", r.message.contact.mobile_no, undefined, true);			
				}

			}
		}
	});
}

var show_address_dialog = function(frm) {
	frm.__onload
	var d = new frappe.ui.Dialog({
		fields: [
			{
				fieldtype: 'Section Break',
				label: __('Primary Address')
			},
			{
				label: __('Address Line 1'),
				fieldname: 'address_line1',
				fieldtype: 'Data',
				default: frm.doc.custom_address_line_1,
				reqd: 1
			},
			{
				label: __('Address Line 2'),
				fieldname: 'address_line2',
				fieldtype: 'Data',
				default: frm.doc.custom_address_line_2
			},
			{
				label: __('ZIP Code'),
				fieldname: 'pincode',
				fieldtype: 'Data',
				default: frm.doc.custom_pincode

			},
			{fieldtype: 'Column Break'},
			{
				label: __('City'),
				fieldname: 'city',
				fieldtype: 'Data',
				default: frm.doc.custom_address_town,
				reqd: 1

			},
			{
				label: __('Country'),
				fieldname: 'country',
				fieldtype: 'Link',
				options: 'Country',
				default: frm.doc.custom_country || "Italy",
				reqd: 1

			},
			{
				fieldtype: 'Section Break',
				label: __('Primary Contact')
			},
			{
				label: __('Email'),
				fieldname: 'email_id',
				fieldtype: 'Data',
				default: frm.doc.custom_email
			},
			{fieldtype: 'Column Break'},
			{
				label: __('Mobile'),
				fieldname: 'mobile_no',
				fieldtype: 'Data',
				default: frm.doc.custom_mobile

			},
			{
				label: __('Phone'),
				fieldname: 'phone',
				fieldtype: 'Data',
				default: frm.doc.custom_phone

			}

		],
		primary_action_label: __('Add'),

		primary_action: () => {
			var values = d.get_values();
			values.name = frm.doc.name;
			if(values) {
				// Update Address and contact then refrehs doc field
				var address = {};
				address.custom_address_line_1 = values.address_line1;
				address.custom_address_line_2= values.address_line2;
				address.custom_pincode= values.pincode;
				address.custom_address_town= values.city;
				address.custom_country= values.country;

				var contact = {};
				contact.custom_phone = values.phone;
				contact.custom_mobile = values.mobile_no;
				contact.custom_email= values.email_id;

				address.name = frm.doc.name;
				contact.name = frm.doc.name;
				frappe.call({
					method: "health_upgrade.health_upgrade.overrides.customer.set_default_address_and_contact_data",
					args: {
						name: frm.doc.name,
						address : address ,
						contact: contact
					},
					callback: function(r){
						if(r){
							d.hide();
							display_default_address_and_contact(frm);
							frappe.show_alert(__('Document updated successfully'));
						}
					}
					});

			}
		}
	});

	return d;
};

