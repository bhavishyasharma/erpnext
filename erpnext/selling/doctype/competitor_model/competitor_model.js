// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Competitor Model', {
	// refresh: function(frm) {

	// }
	brand(frm) {
	    frm.set_query("series", function() {
			return {
				filters: [
					["Competitor Series","brand", "in", [frm.doc.brand]]
				]
			}
		});
	}
});
