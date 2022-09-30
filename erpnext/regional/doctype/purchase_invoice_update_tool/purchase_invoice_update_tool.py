# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class PurchaseInvoiceUpdateTool(Document):
	pass

@frappe.whitelist()
def update_invoice(purchase_invoice, supplier_gstin, supplier_invoice_no):
    try:
        frappe.db.set_value('Purchase Invoice', purchase_invoice, {
            'supplier_gstin': supplier_gstin,
            'bill_no': supplier_invoice_no
        })
    except:
        frappe.throw("Error : Could not update invoice.")
    frappe.msgprint(_("Purchase Invoice {0} updated.").format(purchase_invoice))
