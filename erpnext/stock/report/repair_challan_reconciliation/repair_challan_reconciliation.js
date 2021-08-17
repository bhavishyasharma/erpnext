// Copyright (c) 2016, Bhavishya Sharma and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Repair Challan Reconciliation"] = {
	"filters": [
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		}
	]
}

