# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
	columns = [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"label": "Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
		},
		{
			"label": "Challan",
			"fieldname": "challan",
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
			"label": "Description",
			"ieldname": "description",
			"fieldtype": "Text"
		},
		{
			"label": "Quantity",
			"fieldname": "qty",
			"fieldtype": "Float"
		},
		{
			"label": "Pending Quantity",
			"fieldname": "pending_qty",
			"fieldtype": "Float"
		},
		{
			"label": "Rate",
			"fieldname": "rate",
			"fieldtype": "Currency"
		},
		{
			"label": "Amount",
			"fieldname": "amount",
			"fieldtype": "Currency"
		},
	]
	filter = ""
	if filters and "customer" in filters:
		filter = filter + " and a.customer=\""+filters["supplier"] + "\" "
	if filters and "item_code" in filters:
		filter = filter + " and a.item_code=\""+filters["item_code"] + "\" "
	result = frappe.db.sql("""select a.customer, a.posting_date,
							a.name as challan, b.item_code,
							b.description, b.qty, b.qty-c.returned_qty as pending_qty,
							b.valuation_rate as rate,
							(b.qty-c.returned_qty)*b.valuation_rate as amount
							from `tabStock Entry` a
							left join `tabStock Entry Detail` b
							on a.name = b.parent
							left join (
								select a.ste_detail, a.item_code,
								sum(qty) as returned_qty
								from `tabStock Entry Detail` a
								left join `tabStock Entry` b
								on a.parent = b.name
								where b.stock_entry_type = "Send after Repair"
								group by a.ste_detail
							) c
							on b.name = c.ste_detail
							where a.stock_entry_type = 'Receive for Repair'
							and (c.returned_qty is null or b.qty <> c.returned_qty)
							and a.docstatus=1
							{filter}
				order by a.posting_date""".format(filter=filter))
	return columns, result
