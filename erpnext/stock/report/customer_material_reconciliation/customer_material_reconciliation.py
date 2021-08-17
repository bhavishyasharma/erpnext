# Copyright (c) 2013, Bhavishya Sharma and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"label": "CMI Date",
                        "fieldname": "cmi_Date",
                        "fieldtype": "Date",
		},
		{
                        "label": "CMI Challan",
                        "fieldname": "cmi_challan",
                        "fieldtype": "Link",
                        "options": "Stock Entry"
                },
		{
                        "label": "Item Code",
                        "fieldname": "item_code",
                        "fieldtype": "Link",
                        "options": "Item"
                },
		{
			"label": "Sent Quantity",
			"fieldname": "sent_qty",
			"fieldtype": "Float"
		},
		{
                        "label": "Sent Valuation",
                        "fieldname": "sent_valuation",
                        "fieldtype": "Float"
                },
		{
                        "label": "CMR Date",
                        "fieldname": "cmr_Date",
                        "fieldtype": "Date",
                },
		{
                        "label": "CMR Challan",
                        "fieldname": "cmr_challan",
                        "fieldtype": "Link",
                        "options": "Stock Entry"
                },
                {
                        "label": "Received Quantity",
                        "fieldname": "received_qty",
                        "fieldtype": "Float"
                },
		{
                        "label": "Received Valuation",
                        "fieldname": "received_valuation",
                        "fieldtype": "Float"
                },
		{
                        "label": "Quantity Difference",
                        "fieldname": "qty_diff",
			"fieldtype": "Float"
                },
		{
			"label": "Value Difference",
			"fieldname": "value_diff",
			"fieldtype": "Float"
		}
	]
	filterA = ""
	filterB = ""
	if filters and "customer" in filters:
		filterA = filterA + " and a.customer=\""+filters["customer"] + "\" "
		filterB = filterB + " and b.customer=\""+filters["customer"] + "\" "
	if filters and "item_code" in filters:
		filterA = filterA + " and a.item_code=\""+filters["item_code"] + "\" "
		filterB = filterB + " and a.item_code=\""+filters["item_code"] + "\" "
	result = frappe.db.sql("""(select a.customer, a.cmi_date, a.cmi_challan, a.item_code,
				a.sent_qty, a.sent_valuation, b.cmr_date, b.cmr_challan,
				b.received_qty, b.received_valuation, IFNULL(a.sent_qty,0)-IFNULL(b.received_qty,0) as qty_diff,
				IFNULL(a.sent_qty,0)*IFNULL(a.sent_valuation,0)-IFNULL(b.received_qty,0)*IFNULL(b.received_valuation,0) as value_diff
				from
					(select b.customer, b.posting_date as cmi_date, a.parent as cmi_challan, a.name as cmi_item,
					a.item_code, a.qty as sent_qty, a.valuation_rate as sent_valuation, a.return_stock_entry_item
					from `tabStock Entry Detail` a
					left join `tabStock Entry` b
					on a.parent = b.name
					where
						a.parent like '%CMI-%' and
						(b.warranty_status is null or b.warranty_status = 'Out of Warranty') and
						a.docstatus=1 and b.docstatus=1
					order by b.posting_date) a
				left join
					(select b.customer, b.posting_date as cmr_date, a.parent as cmr_challan,
					a.name as cmr_item, a.item_code, a.qty as received_qty,
					a.valuation_rate as received_valuation
					from `tabStock Entry Detail` a
					left join `tabStock Entry` b
					on a.parent = b.name
					where
						a.parent like '%CMR-%'
						and a.docstatus=1 and b.docstatus=1
					order by b.posting_date) b
				on a.return_stock_entry_item = b.cmr_item
				where (a.item_code is not null or b.item_code is not null)
				{filter1}
				)
				union
				(select b.customer, null as cmi_date, null as cmi_challan, a.item_code, null as sent_qty, null as sent_valuation,
				b.posting_date as cmr_date, a.parent as cmr_challan, a.qty as received_qty,
				a.valuation_rate as received_valuation, 0-IFNULL(a.qty,0) as qty_diff, 0-IFNULL(a.qty,0)*IFNULL(a.valuation_rate,0) as value_diff
				from `tabStock Entry Detail` a
				left join `tabStock Entry` b
				on a.parent = b.name
				where a.parent like '%CMR-%'
					and (b.warranty_status is null or b.warranty_status = 'Out of Warranty')
					and a.docstatus=1 and b.docstatus=1 and
					a.name not in (
							select distinct(return_stock_entry_item)
							from `tabStock Entry Detail`
							where return_stock_entry_item is not null
							and docstatus=1)
					{filter2}
				order by b.posting_date) order by cmr_date, cmi_date""".format(filter1=filterA, filter2=filterB))
	return columns, result
