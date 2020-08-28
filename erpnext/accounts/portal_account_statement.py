import frappe

@frappe.whitelist()
def get_portal_account_statement(customer, fiscal_year):
    year = frappe.get_doc("Fiscal Year", fiscal_year)
    user = frappe.session.user
    contacts = frappe.db.sql("""
		    select
				`tabContact`.email_id,
				`tabDynamic Link`.link_doctype,
				`tabDynamic Link`.link_name
			from
				`tabContact`, `tabDynamic Link`
			where
				`tabContact`.name=`tabDynamic Link`.parent and `tabContact`.email_id =%s
			""", user, as_dict=1)
    has_permission = False
    customers = [c.link_name for c in contacts if c.link_doctype == 'Customer']
    for c in customers:
        if c == customer:
            has_permission = True
            break
    if not has_permission:
        frappe.msgprint("You dont have permission for this account")
    else:
        from erpnext.accounts.report.general_ledger.general_ledger import execute as get_ledger
        report_filters = frappe._dict({'company': frappe.defaults.get_user_default("Company"),
            'from_date': str(year.year_start_date),
            'to_date': str(year.year_end_date),
            'party_type': 'Customer',
            'party': [customer],
            'group_by': 'Group by Voucher (Consolidated)',
            'cost_center': [], 'project': [],
            'include_default_book_entries': 1})
        columns, res = get_ledger(filters=report_filters)
        columns = [
            'Id', 'Posting Date', 'Type', 'Voucher', 'Debit', 'Credit', 'Balance'
        ]
        res[0]['voucher_type'] = str(res[0]['account'])[1:-1]
        res[-1]['voucher_type'] = str(res[-1]['account'])[1:-1]
        res[-2]['voucher_type'] = str(res[-2]['account'])[1:-1]
        return res
