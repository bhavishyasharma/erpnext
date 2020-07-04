// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Competition Comparison', {
	// refresh: function(frm) {

	// }
	get_comparison: function(frm) {
		if(frm.doc.models.length <= 1) {
			frappe.throw("Please select atleast 2 models");
		}
		else {
			frappe.call({
				"method" : "erpnext.selling.doctype.competition_comparison.competition_comparison.get_comparison",
				"args" : {
					models: frm.doc.models.map((model) => {return model.model})
				},
				"callback": function(r) {
					let data = r.message;
					console.log(data);
					frappe.ui.get_print_settings(false, print_settings => {
						console.log(print_settings);
						frappe.render_grid({
							template: 'competition_comparison',
							title: 'Competition Comparison',
							print_settings: print_settings,
							data: data,
							columns: []
						});
					});
				}
			});
		}
	}
});
