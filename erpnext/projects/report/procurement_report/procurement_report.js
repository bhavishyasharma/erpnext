// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Procurement Report"] = {
	"filters": [

	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if(column.colIndex>1){
			if(data[column.fieldname].status==="Completed"){
				if(data[column.fieldname].act_end_date){
					value = data[column.fieldname].act_end_date;
				}
				else{
					value = data[column.fieldname].end_date;
				}
				value = "<span style='color:green;font-weight:bold';>" + value + " / " + data[column.fieldname].status + "</span>";
			}
			else if(data[column.fieldname].status==="Working"){
				value = "<span style='color:orange;font-weight:bold';>" + data[column.fieldname].end_date + " / " + data[column.fieldname].status + "</span>";
			}
			else if(data[column.fieldname].status==="Overdue"){
				value = "<span style='color:red;font-weight:bold';>" + data[column.fieldname].end_date + " / " + data[column.fieldname].status + "</span>";
			}
			else if(data[column.fieldname].end_date){
				value = "<span style='color:blue;font-weight:bold';>" + data[column.fieldname].end_date + " / " + data[column.fieldname].status + "</span>";
			}
			else {
				value = "";
			}
		}
		return value;
	}
};
