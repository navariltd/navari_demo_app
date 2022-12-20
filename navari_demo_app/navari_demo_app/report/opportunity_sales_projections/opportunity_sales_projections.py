# Copyright (c) 2022, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import add_to_date

def execute(filters=None):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))
	return get_columns(), get_data(filters)

def get_data(filters):
	company, from_date, to_date, opportunity_owner, opportunity_id = filters.get('company'), filters.get('from_date'), filters.get('to_date'), filters.get('opportunity_owner'), filters.get('opportunity_id')

	# conditions (used with filters)
	conditions = " AND 1=1 "
	
	if(filters.get('company')):
		conditions += f" AND company = '{company}'"
	if(filters.get('opportunity_owner')):
		conditions += f" AND opportunity_owner = '{opportunity_owner}'"
	if(filters.get('opportunity_id')):
		conditions += f" AND name LIKE '%{opportunity_id}'"

	opportunities = frappe.db.sql(f"""
		SELECT opportunity_owner, name, expected_closing, lead_time_days
		FROM `tabOpportunity`
		WHERE (expected_closing BETWEEN '{from_date}' AND '{to_date}') {conditions}
	""", as_dict = 1)

	# Create list, equal length as rows fetched
	report_details = [None] * len(opportunities)

	for opportunity in opportunities:
		report_details[opportunities.index(opportunity)] = list(opportunity.values())

		recommended_purchase_date = add_to_date(opportunity.expected_closing, days = -abs(opportunity.lead_time_days), as_datetime=True)
		report_details[opportunities.index(opportunity)].append(recommended_purchase_date)

		# item_details is a multidimensional array, fixing this to appear on UI
		item_details = frappe.db.sql(f"""SELECT item_code, item_name, uom, SUM(qty) as qty FROM `tabOpportunity Item` WHERE parent = '{opportunity.name}' GROUP BY item_code, item_name, uom;""", as_list = 1)
		report_details[opportunities.index(opportunity)].append(item_details)

		# Fetch lead time data, transpose rows to columns.
		lead_time_details = frappe.db.sql(f"""
			SELECT
				MAX(CASE WHEN `tabOpportunity Lead Time Item`.lead_time_category = 'Supply' THEN `tabOpportunity Lead Time Item`.lead_time_in_days END)  AS 'Supply',
				MAX(CASE WHEN `tabOpportunity Lead Time Item`.lead_time_category = 'Shipping' THEN `tabOpportunity Lead Time Item`.lead_time_in_days END) AS 'Shipping',
				MAX(CASE WHEN `tabOpportunity Lead Time Item`.lead_time_category = 'Port Clearance' THEN `tabOpportunity Lead Time Item`.lead_time_in_days END) AS 'Port Clearance'
				FROM `tabOpportunity Lead Time Item`
				WHERE parent = '{opportunity.name}';
		""", as_list = 1)
		lead_time_details = lead_time_details[0]
		# Adding Supply, Shipping and Port Clearance days to the list, in that order
		report_details[opportunities.index(opportunity)].append(lead_time_details[0])
		report_details[opportunities.index(opportunity)].append(lead_time_details[1])
		report_details[opportunities.index(opportunity)].append(lead_time_details[2])

	return report_details

def get_columns():
	return [
		{
            'fieldname': 'opportunity_owner',
            'label': _('User'),
            'fieldtype': 'Link',
            'options': 'User'
        },
		{
            'fieldname': 'name',
            'label': _('Opportunity'),
            'fieldtype': 'Data',
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
			'fieldname': 'items',
			'label': _('Items'),
			'fieldtype': 'Table',
			'columns': [
				{
					'fieldname': 'item_code',
					'label': _('Item'),
					'fieldtype': 'Link',
					'options': 'Item'
				},
				{
					'fieldname': 'item_name',
					'label': _('Item Name'),
					'fieldtype': 'Data',
				},
				{
					'fieldname': 'uom',
					'label': _('UOM'),
					'fieldtype': 'Link',
					'options': 'UOM'
				},
				{
					'fieldname': 'qty',
					'label': _('Qty'),
					'fieldtype': 'Float',
				}
			]
		},
		{
            'fieldname': 'supply',
            'label': _('Supply Days'),
            'fieldtype': 'Int',
        },
		{
            'fieldname': 'shipping',
            'label': _('Shipping Days'),
            'fieldtype': 'Int',
        },
		{
            'fieldname': 'port_clearance',
            'label': _('Port Clearance Days'),
            'fieldtype': 'Int',
        }
	]

