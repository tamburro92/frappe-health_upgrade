// Copyright (c) 2023, Tamburro and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Daily Patient Appointments"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"mark_overlapping_appointments",
			"label": __("Show Overlap"),
			"fieldtype": "Check",
			"default": 1
		}
	],
	
	// If two appointments for different doctors require a nurse on the same time slot, show them in red text color.
	"formatter": function(value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		// if overlaps_with has a value, make the text red and bold
		if(data){

			if (data.overlaps_with && data.mark_overlapping_appointments) {

				if (value.indexOf('grey') != -1) {
					var $value = $(value).removeClass('grey');
					value = $value.wrapInner("<span style='color:#ff0033!important;font-weight:bold'></span>").wrap("<p></p>").parent().html();
				} else {
					value = "<span style='color:#ff0033!important;font-weight:bold'>" +  value +  "</span>"
				}

			} else if (data.requires_nurse && data.mark_overlapping_appointments) {

				if (value.indexOf('grey') != -1) {
					var $value = $(value).removeClass('grey');
					value = $value.wrapInner("<span style='color:salmon!important;font-weight:bold'></span>").wrap("<p></p>").parent().html();
				} else {
					value = "<span style='color:salmon!important;font-weight:bold'>" +  value +  "</span>"
				}

			} 


			if(data && data.procedure_room == "Stanza 2"){

				if (value.indexOf('grey') != -1) {
					var $value = $(value).removeClass('grey');
					value = $value.wrapInner("<span style='color:blue!important;font-weight:bold'></span>").wrap("<p></p>").parent().html();
				} else {
					value = "<span style='color:blue!important;font-weight:bold'>" +  value +  "</span>"
				}	

			} else if( data && data.color != "#000000"  ){

				if (value.indexOf('grey') != -1) {
					var $value = $(value).removeClass('grey');
					value = $value.wrapInner(`<span style='color:${data.color}!important;font-weight:bold'></span>`).wrap("<p></p>").parent().html();
				} else {
					value = `<span style='color:${data.color}!important;font-weight:bold'>` +  value +  "</span>"

				}
				
			} else if ( data && data.item_color != "#000000" ) {

				if (value.indexOf('grey') != -1) {
					var $value = $(value).removeClass('grey');
					value = $value.wrapInner(`<span style='color:${data.item_color}!important;font-weight:bold'></span>`).wrap("<p></p>").parent().html();
				} else {
					value = `<span style='color:${data.item_color}!important;font-weight:bold'>` +  value +  "</span>"

				}

			}
		}

		return value
	}
}