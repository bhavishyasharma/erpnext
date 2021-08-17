// Copyright (c) 2016, Bhavishya Sharma and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Material Reconciliation"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		}
	]
}
