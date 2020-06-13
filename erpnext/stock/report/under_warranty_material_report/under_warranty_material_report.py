# Copyright (c) 2013, Bhavishya Sharma and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	if from_date > to_date:
		frappe.throw(_("From Date must be before To Date"))
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
                        "fieldname": "description",
                        "fieldtype": "Text"
                },
		{
			"label": "Quantity",
			"fieldname": "qty",
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
							b.description, b.qty, b.valuation_rate as rate,
							b.amount
							from `tabStock Entry` a
							left join `tabStock Entry Detail` b
							on a.name = b.parent
							where a.stock_entry_type = 'Issue Under Warranty'
							and a.docstatus=1
							and a.posting_date >=%(from_date)s
							and a.posting_date <=%(to_date)s
					{filter}
				order by a.posting_date""".format(filter=filter),{
								'from_date': from_date,
								'to_date': to_date
							})
	return columns, result
