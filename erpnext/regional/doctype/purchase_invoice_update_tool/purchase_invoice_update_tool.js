// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice Update Tool', {
	// refresh: function(frm) {

	// }
        update_invoice(frm) {
            frm.call({
                    method: 'erpnext.regional.doctype.purchase_invoice_update_tool.purchase_invoice_update_tool.update_invoice',
                    args: {
                        purchase_invoice: frm.doc.purchase_invoice,
                        supplier_gstin: frm.doc.supplier_gstin,
                        supplier_invoice_no: frm.doc.supplier_invoice_no
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
});
