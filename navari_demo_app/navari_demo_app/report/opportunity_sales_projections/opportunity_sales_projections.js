// Copyright (c) 2022, Navari Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Opportunity Sales Projections"] = {
	
	"filters": [
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
			fieldname: "opportunity_id",
			label: __("Opportunity"),
			fieldtype: "Link",
			options: "Opportunity",
			reqd: 0
		},
		{
			fieldname: "opportunity_owner",
			label: __("Opportunity owner"),
			fieldtype: "Link",
			options: "User",
			reqd: 0
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		}
	]
};
