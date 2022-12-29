// Copyright (c) 2022, Navari Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Opportunity Sales Projections"] = {
	
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_start_date"),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_end_date"),
			reqd: 1
		},
		{
			fieldname: "opportunity_owner",
			label: __("Opportunity owner"),
			fieldtype: "Link",
			options: "User",
			reqd: 0
		},
		{
			fieldname: "opportunity_id",
			label: __("Opportunity"),
			fieldtype: "Link",
			options: "Opportunity",
			reqd: 0
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data)
	
		if (column.fieldname == "recommended_purchase_date") {
			if(value) {
				let date_array = value.split("-")
				let [day, month, year] = date_array
				// re-arrange date fornat so we can pass to new Date() function
				let date_string = `${year}-${month}-${day}`
				let recommended_purchase_date = new Date(date_string)
				let today = new Date()
				

				if(recommended_purchase_date.getTime() < today.getTime()) {
					value = "<span style='color:red;'>" + value + "</span>"
				}

				if(recommended_purchase_date.getTime() > today.getTime()) {
					value = "<span style='color:green;'>" + value + "</span>"
				}

				if(recommended_purchase_date.getTime() == today.getTime()) {
					value = "<span style='color:orange;'>" + value + "</span>"
				}
			}
		}
		return value
	}
};
