# Copyright (c) 2019, Frappe and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe


def execute():
    frappe.reload_doc("manufacturing", "doctype", "job_card")
    frappe.reload_doc("manufacturing", "doctype", "job_card_item")
    frappe.reload_doc("stock", "doctype", "stock_entry")
    frappe.reload_doc("stock", "doctype", "stock_entry_detail")

    stes = frappe.db.get_list('Stock Entry', filters={ 'docstatus': 1, 'stock_entry_type': 'Material Transfer for Manufacture' }, fields=['name', 'job_card'])
    count = 0
    for ste in stes:
        if ste.job_card:
            ste_doc = frappe.get_doc('Stock Entry', ste.name)
            job_doc = frappe.get_doc('Job Card', ste.job_card)
            job_doc.set_transferred_qty(update_status=True)
            job_doc.set_transferred_qty_in_job_card(ste_doc)
            frappe.db.commit()
        count += 1
        print("""{0} / {1} Stock Entries processesd...""".format(count, len(stes)), end='\r')
        
