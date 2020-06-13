import frappe
from frappe import _
from frappe.utils.user import is_website_user

def get_context(context):
    context.no_cache = 1
    context.title = 'Account Statement'
    context.show_sidebar = True
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
    customers = [c.link_name for c in contacts if c.link_doctype == 'Customer']
    ignore_permissions = False
    years = frappe.db.sql("""select name from `tabFiscal Year`""")
    context.customers = customers
    context.years = [year[0] for year in years]