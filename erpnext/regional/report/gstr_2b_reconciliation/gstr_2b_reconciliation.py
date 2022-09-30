# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import flt
import erpnext.accounts.report.purchase_register.purchase_register as pr
import json

def execute(filters=None):
	if not filters: filters = {}
	additional_table_columns = [
		dict(fieldtype='Data', label='Supplier GSTIN', fieldname="supplier_gstin", width=120),
		dict(fieldtype='Data', label='Reverse Charge', fieldname="reverse_charge", width=120),
		dict(fieldtype='Data', label='GST Category', fieldname="gst_category", width=120),
	]
	additional_query_columns = [
		'supplier_gstin',
		'reverse_charge',
		'gst_category'
	]

	invoice_list = pr.get_invoices(filters, additional_query_columns + ['is_return'])
	columns, expense_accounts, tax_accounts, unrealized_profit_loss_accounts \
		= get_columns(invoice_list, additional_table_columns)

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	invoice_expense_map = pr.get_invoice_expense_map(invoice_list)
	internal_invoice_map = pr.get_internal_invoice_map(invoice_list)
	invoice_expense_map, invoice_tax_map = pr.get_invoice_tax_map(invoice_list,
		invoice_expense_map, expense_accounts)
	invoice_po_pr_map = pr.get_invoice_po_pr_map(invoice_list)
	suppliers = list(set(d.supplier for d in invoice_list))
	supplier_details = pr.get_supplier_details(suppliers)

	company_currency = frappe.get_cached_value('Company',  filters.company,  "default_currency")

	portal_invoice_list = frappe.db.sql("""select
			gstin_of_supplier, tradelegal_name, invoice_number, invoice_date,
			supply_attract_reverse_charge, itc_availability,
			sum(taxable_value) as total_taxable_value,
			sum(integrated_tax) as total_igst, sum(central_tax) as total_cgst,
			sum(stateut_tax) as total_sgst, sum(invoice_value) as total_invoice_value
			from `tabPortal GSTR 2B Invoice Entry`
			group by gstin_of_supplier, invoice_number
			order by tradelegal_name""", as_dict=1)

	portal_invoices = {}
	for inv in portal_invoice_list:
		portal_invoices[(inv['gstin_of_supplier'], inv['invoice_number'])] = inv


	columns += [_('Portal Reverse Charge') + "::100",
				_('ITC Availability') + "::60",
				_('Taxable Value') + ":Currency/currency:120",
				_('IGST ITC') + ":Currency/currency:120",
                _('CGST ITC') + ":Currency/currency:120",
				_('SGST ITC') + ":Currency/currency:120",
				_('Total Value') + ":Currency/currency:120",
				_('IGST Difference') + ":Currency/currency:120",
				_('CGST Difference') + ":Currency/currency:120",
				_('SGST Difference') + ":Currency/currency:120"]

	data = []
	for inv in invoice_list:
		row = [inv.name, inv.posting_date, inv.supplier, inv.supplier_name]

		if inv.get('gst_category')=='Overseas':
			continue
		if additional_query_columns:
			for col in additional_query_columns:
				row.append(inv.get(col))

		row += [
			inv.bill_no, inv.bill_date
		]

		base_net_total = 0
		for expense_acc in expense_accounts:
			if inv.is_internal_supplier and inv.company == inv.represents_company:
				expense_amount = 0
			else:
				expense_amount = flt(invoice_expense_map.get(inv.name, {}).get(expense_acc))
			base_net_total += expense_amount

		row.append(base_net_total or inv.base_net_total)
		total_tax = 0
		igst_amount = cgst_amount = sgst_amount = 0
		for tax_acc in tax_accounts:
			if tax_acc not in expense_accounts:
				tax_amount = flt(invoice_tax_map.get(inv.name, {}).get(tax_acc))
				if tax_acc in ['IGST - BST', 'Reverse Charge IGST Payable - BST']:
					igst_amount += tax_amount
				elif tax_acc in ['CGST - BST', 'Reverse Charge CGST Payable - BST']:
					cgst_amount += tax_amount
				elif tax_acc in ['SGST - BST', 'Reverse Charge SGST Payable - BST']:
					sgst_amount += tax_amount
				total_tax += tax_amount
				row.append(tax_amount)

		row += [total_tax, inv.base_grand_total, flt(inv.base_grand_total, 0)]

		key = (inv['supplier_gstin'], inv['bill_no'])
		if portal_invoices.get(key) and not inv['is_return']:
			portal_invoice = portal_invoices[key]
			row.append(portal_invoice['supply_attract_reverse_charge'] or '')
			row.append(portal_invoice['itc_availability'] or '')
			row.append(portal_invoice['total_taxable_value'] or 0)
			if portal_invoice['itc_availability']=='Yes':
				row.append(portal_invoice['total_igst'] or 0)
				row.append(portal_invoice['total_cgst'] or 0)
				row.append(portal_invoice['total_sgst'] or 0)
			else:
				row.append(0)
				row.append(0)
				row.append(0)
			row.append(portal_invoice['total_invoice_value'] or 0)
			if portal_invoice['supply_attract_reverse_charge'] != 'Yes': 
				if portal_invoice['itc_availability']=='Yes':
					row.append(igst_amount - (portal_invoice['total_igst'] or 0))
					row.append(cgst_amount - (portal_invoice['total_cgst'] or 0))
					row.append(sgst_amount - (portal_invoice['total_sgst'] or 0))
					row[-1] = round(row[-1])
					row[-2] = round(row[-2])
					row[-3] = round(row[-3])
				else:
					row.append(igst_amount)
					row.append(cgst_amount)
					row.append(sgst_amount)
			else:
				row.append(igst_amount)
				row.append(cgst_amount)
				row.append(sgst_amount)
			del portal_invoices[key]
		else:
			row += ['','','','','','','','','','']
		if row[-1] == 0 and row[-2] == 0 and row[-3] == 0:
			continue
		data.append(row)

	for key in portal_invoices:
		portal_invoice = portal_invoices[key]
		row = ['', '', '', portal_invoice['tradelegal_name'], portal_invoice['gstin_of_supplier'],
				'', '', portal_invoice['invoice_number'], portal_invoice['invoice_date'], 
				portal_invoice['total_taxable_value'], '']
		for tax_acc in tax_accounts:
			if tax_acc not in expense_accounts:
				row.append('')
		row += ['','']
		row.append(portal_invoice['supply_attract_reverse_charge'] or '')
		row.append(portal_invoice['itc_availability'] or '')
		row.append(portal_invoice['total_taxable_value'] or 0)
		row.append(portal_invoice['total_igst'] or 0)
		row.append(portal_invoice['total_cgst'] or 0)
		row.append(portal_invoice['total_sgst'] or 0)
		row.append(portal_invoice['total_invoice_value'] or 0)
		row.append(-portal_invoice['total_igst'] or 0)
		row.append(-portal_invoice['total_cgst'] or 0)
		row.append(-portal_invoice['total_sgst'] or 0)

		data.append(row)

	return columns, data

def get_columns(invoice_list, additional_table_columns):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Purchase Invoice:120", _("Posting Date") + ":Date:80",
		_("Supplier Id") + "::120", _("Supplier Name") + "::120"]

	if additional_table_columns:
		columns += additional_table_columns

	columns += [
		_("Bill No") + "::120", _("Bill Date") + ":Date:80"
	]
	expense_accounts = tax_accounts = expense_columns = tax_columns = unrealized_profit_loss_accounts = \
		unrealized_profit_loss_account_columns = []

	if invoice_list:
		expense_accounts = frappe.db.sql_list("""select distinct expense_account
			from `tabPurchase Invoice Item` where docstatus = 1
			and (expense_account is not null and expense_account != '')
			and parent in (%s) order by expense_account""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

		tax_accounts = 	frappe.db.sql_list("""select distinct account_head
			from `tabPurchase Taxes and Charges` where parenttype = 'Purchase Invoice'
			and docstatus = 1 and (account_head is not null and account_head != '')
			and category in ('Total', 'Valuation and Total')
			and parent in (%s) order by account_head""" %
			', '.join(['%s']*len(invoice_list)), tuple(inv.name for inv in invoice_list))

		unrealized_profit_loss_accounts = frappe.db.sql_list("""SELECT distinct unrealized_profit_loss_account
			from `tabPurchase Invoice` where docstatus = 1 and name in (%s)
			and ifnull(unrealized_profit_loss_account, '') != ''
			order by unrealized_profit_loss_account""" %
			', '.join(['%s']*len(invoice_list)), tuple(inv.name for inv in invoice_list))

	expense_columns = [(account + ":Currency/currency:120") for account in expense_accounts]
	unrealized_profit_loss_account_columns = [(account + ":Currency/currency:120") for account in unrealized_profit_loss_accounts]

	for account in tax_accounts:
		if account not in expense_accounts:
			tax_columns.append(account + ":Currency/currency:120")

	columns = columns + \
		[_("Net Total") + ":Currency/currency:120"] + tax_columns + \
		[_("Total Tax") + ":Currency/currency:120", _("Grand Total") + ":Currency/currency:120",
			_("Rounded Total") + ":Currency/currency:120"]

	return columns, expense_accounts, tax_accounts, unrealized_profit_loss_accounts