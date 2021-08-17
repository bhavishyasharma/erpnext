# Copyright (c) 2013, Bhavishya Sharma and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{
			"label": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"label": "RPC Date",
                        "fieldname": "rpc_Date",
                        "fieldtype": "Date",
		},
		{
                        "label": "RPC Challan",
                        "fieldname": "rpc_challan",
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
                        "label": "RPC Description",
                        "fieldname": "rpc_description",
                        "fieldtype": "Text"
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
                        "label": "RPC RET Date",
                        "fieldname": "rpc_ret_Date",
                        "fieldtype": "Date",
                },
		{
                        "label": "RPC-RET Challan",
                        "fieldname": "rpc_ret_challan",
                        "fieldtype": "Link",
                        "options": "Stock Entry"
                },
		{
                        "label": "RPC RET Description",
                        "fieldname": "rpc_ret_description",
                        "fieldtype": "Text"
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
	if filters and "supplier" in filters:
		filterA = filterA + " and a.supplier=\""+filters["supplier"] + "\" "
		filterB = filterB + " and b.supplier=\""+filters["supplier"] + "\" "
	if filters and "item_code" in filters:
		filterA = filterA + " and a.item_code=\""+filters["item_code"] + "\" "
		filterB = filterB + " and a.item_code=\""+filters["item_code"] + "\" "
	result = frappe.db.sql("""(select a.supplier, a.rpc_date, a.rpc_challan, a.item_code, a.rpc_description,
				a.sent_qty, a.sent_valuation, b.rpc_ret_date, b.rpc_ret_challan, b.rpc_ret_description,
				b.received_qty, b.received_valuation, IFNULL(a.sent_qty,0)-IFNULL(b.received_qty,0) as qty_diff,
				IFNULL(a.sent_qty,0)*IFNULL(a.sent_valuation,0)-IFNULL(b.received_qty,0)*IFNULL(b.received_valuation,0) as value_diff
				from
					(select b.supplier, b.posting_date as rpc_date, a.parent as rpc_challan, a.name as rpc_item,
					a.item_code, concat(a.description,": ",a.name) as rpc_description, a.qty as sent_qty, a.valuation_rate as sent_valuation, a.return_stock_entry_item
					from `tabStock Entry Detail` a
					left join `tabStock Entry` b
					on a.parent = b.name
					where
						a.parent like '%RPC-%' and
						a.parent not like '%RPC-RET-%'
						and a.docstatus=1 and b.docstatus=1
					order by b.posting_date) a
				left join
					(select b.supplier, b.posting_date as rpc_ret_date, a.parent as rpc_ret_challan,
					a.name as rpc_ret_item, a.description as rpc_ret_description, a.item_code, a.qty as received_qty,
					a.valuation_rate as received_valuation
					from `tabStock Entry Detail` a
					left join `tabStock Entry` b
					on a.parent = b.name
					where
						a.parent like '%RPC-RET-%'
						and a.docstatus=1 and b.docstatus=1
					order by b.posting_date) b
				on a.return_stock_entry_item = b.rpc_ret_item
				where (a.item_code is not null or b.item_code is not null)
				{filter1}
				)
				union
				(select b.supplier, null as rpc_date, null as rpc_challan, a.item_code as item_code, null as rpc_description, null as sent_qty, null as sent_valuation,
				b.posting_date as rpc_ret_date, a.parent as rpc_ret_challan, concat(a.description,": ",a.name) as rpc_ret_description, a.qty as received_qty,
				a.valuation_rate as received_valuation, 0-IFNULL(a.qty,0) as qty_diff, 0-IFNULL(a.qty,0)*IFNULL(a.valuation_rate,0) as value_diff
				from `tabStock Entry Detail` a
				left join `tabStock Entry` b
				on a.parent = b.name
				where a.parent like '%RPC-RET-%'
					and a.docstatus=1 and b.docstatus=1 and
					a.name not in (
							select distinct(return_stock_entry_item)
							from `tabStock Entry Detail`
							where return_stock_entry_item is not null
							and docstatus=1)
					{filter2}
				order by b.posting_date) order by rpc_ret_date, rpc_date""".format(filter1=filterA, filter2=filterB))
	return columns, result
