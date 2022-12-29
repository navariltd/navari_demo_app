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
			DATE_SUB(opp.expected_closing, INTERVAL IFNULL(opp.lead_time_days,0) DAY) as "recommended_purchase_date"
		FROM `tabOpportunity` as opp
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
				opportunity[f'{field_name}'] = lead_time_details[category.Category]	

		items = frappe.db.sql(f"""
			SELECT item_code as 'item',
				uom as 'uom',
				qty as 'qty'
			FROM `tabOpportunity Item` WHERE parent = '{opportunity.name}';
		""", as_dict = 1)
		# item line qty (sum all item qty for an opportunity)
		total_qty = 0
		
		for item in items:
			total_qty += int(item['qty'])
			item['indent'] = 1
			report_details.append(item)
		opportunity['qty'] = total_qty
		total_qty = 0

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
			'fieldtype': 'Link',
			'options': 'Opportunity'
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
		}
	]

	for category in lead_time_categories:
		field_name = category.Category.lower().replace(" ", "_")
		columns += [
			{
				'label': _(category.Category),
				'fieldname': field_name,
				'fieldtype': 'Data',
				'width': 150

			}
		]

	columns += [
		{
			'fieldname': 'lead_time_days',
			'label': _('Total Lead Time Days'),
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

	return columns
	

