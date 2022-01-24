// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('OpenBOM Import Tool', {
	refresh: function(frm) {

	},
	
	process_file(frm) {
		frm.call({
				method: 'erpnext.manufacturing.doctype.openbom_import_tool.openbom_import_tool.process_open_bom',
				args: {
					import_file: frm.doc.bom_file
				},
				error_handlers: {
					TimestampMismatchError() {
						// ignore this error
					}
				}
			})
			.then(r => {
				
			});
	},
	import_bom(frm) {
		if(!frm.doc.item_code){
			frappe.throw(__("Please set an Item."));
		}
		else{
			frm.call({
					method: 'erpnext.manufacturing.doctype.openbom_import_tool.openbom_import_tool.import_open_bom',
					args: {
						import_file: frm.doc.bom_file,
						item_code: frm.doc.item_code
					},
					error_handlers: {
						TimestampMismatchError() {
							// ignore this error
						}
					}
				})
				.then(r => {
				
				});
		}
	}
});
