// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GSTR 2B Reconciliation"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		}
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		console.log(data);
		if (data["igst_difference"] > 1 || data["igst_difference"] < -1 || data["cgst_difference"] > 1 || data["cgst_difference"] < -1 || data["sgst_difference"] > 1 || data["sgst_difference"] < -1) {
			value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
		}
		else if(data["igst_difference"] === "" || data["igst_difference"] === null){
			value = "<span style='color:orange!important;font-weight:bold'>" + value + "</span>";
		}
		return value;
	}
};
