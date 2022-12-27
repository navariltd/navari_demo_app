# Copyright (c) 2022, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import add_to_date

lead_time_categories = frappe.db.sql(f"""
	SELECT DISTINCT lead_time_category as Category
	FROM `tabOpportunity Lead Time Item`
	ORDER BY Category ASC;
""", as_dict = 1)

def execute(filters=None):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))
	return get_columns(), get_data(filters)

def get_data(filters):
	company, from_date, to_date, opportunity_owner, opportunity_id = filters.get('company'), filters.get('from_date'), filters.get('to_date'), filters.get('opportunity_owner'), filters.get('opportunity_id')
	report_details = []

	conditions = " AND 1=1 "
	
	if(company):
		conditions += f" AND opp.company = '{company}'"
	if(opportunity_owner):
		conditions += f" AND opp.opportunity_owner = '{opportunity_owner}'"
	if(opportunity_id):
		conditions += f" AND opp.name LIKE '%{opportunity_id}'"

	opportunities = frappe.db.sql(f"""
		SELECT opp.company as "company",
			opp.name as "name",
			opp.contact_person as "contact_person",
			opp.customer_name as "customer_name",
			opp.opportunity_owner as "opportunity_owner",
			opp.expected_closing as "expected_closing",
			opp.lead_time_days as "lead_time_days",
			DATE_SUB(opp.expected_closing, INTERVAL IFNULL(opp.lead_time_days,0) DAY) as "recommended_purchase_date",
			opp_item.item_code as "item",
			opp_item.uom as "uom",
			opp_item.qty as "qty"
		FROM `tabOpportunity` as opp
			INNER JOIN `tabOpportunity Item` as opp_item ON opp_item.parent = opp.name
		WHERE (opp.expected_closing BETWEEN '{from_date}' AND '{to_date}') {conditions}
		ORDER BY opp.expected_closing;
	""", as_dict = 1)

	for opportunity in opportunities:
		report_details.append(opportunity)

		categories = frappe.db.sql(f"""
			SELECT lead_time_category as Category
			FROM `tabOpportunity Lead Time Item` WHERE parent = '{opportunity.name}' ORDER BY Category ASC;
		""", as_dict = 1)

		if (categories):
			query_string = "SELECT"

			for category in categories:
				query_string += f" MAX(CASE WHEN `tabOpportunity Lead Time Item`.lead_time_category = '{category.Category}' THEN `tabOpportunity Lead Time Item`.lead_time_in_days END)  AS '{category.Category}',"

			query_string = query_string.rstrip(',')
			query_string += f" FROM `tabOpportunity Lead Time Item` WHERE parent = '{opportunity.name}';"

			lead_time_details = frappe.db.sql(f"""
				{query_string}
			""", as_dict = 1)
			lead_time_details = lead_time_details[0]

			for category in categories:
				# field name  we'll use to map to a column
				field_name = category.Category.lower().replace(" ", "_")
				report_details[opportunities.index(opportunity)][f'{field_name}'] = lead_time_details[category.Category]

	return report_details

def get_columns():
	columns = [
		{
			'fieldname': 'company',
			'label': _('Company'),
			'fieldtype': 'Link',
			'options': 'Company'
		},
		{
			'fieldname': 'name',
			'label': _('Opportunity'),
			'fieldtype': 'Data',
		},
		{
			'fieldname': 'contact_person',
			'label': _('Contact Person'),
			'fieldtype': 'Link',
			'options': 'User',
			'width': 150
		},
		{
			'fieldname': 'customer_name',
			'label': _('Customer Name'),
			'fieldtype': 'Data',
			'width': 150
		},
		{
			'fieldname': 'opportunity_owner',
			'label': _('User'),
			'fieldtype': 'Link',
			'options': 'User',
			'width': 200
		},
		{
			'fieldname': 'expected_closing',
			'label': _('Closing Date'),
			'fieldtype': 'Date',
		},
		{
			'fieldname': 'lead_time_days',
			'label': _('Lead Time Days'),
			'fieldtype': 'Int',
		},
		{
			'fieldname': 'recommended_purchase_date',
			'label': _('Recommended Purchase Date'),
			'fieldtype': 'Date',
		},
		{
			'fieldname': 'item',
			'label': _('Item'),
			'fieldtype': 'Link',
			'options': 'Item',
			'width': 240
		},
		{
			'fieldname': 'uom',
			'label': _('UOM'),
			'fieldtype': 'Link',
			'options': 'UOM',
			'width': 100
		},
		{
			'fieldname': 'qty',
			'label': _('Qty'),
			'fieldtype': 'Float',
			'width': 100
		}
	]

	for category in lead_time_categories:
		field_name = category.Category.lower().replace(" ", "_")
		columns += [
			{
				"label": _(category.Category),
				"fieldname": field_name,
				"fieldtype": "Data",
			}
		]

	return columns
	

