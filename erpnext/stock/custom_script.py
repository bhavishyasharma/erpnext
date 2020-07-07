import frappe
import datetime
import traceback
import frappe.utils as utils
from pprint import pprint
import copy

def complete_work_order(work_order):
	if work_order is None:
		return None
	jcs = frappe.get_list('Job Card', filters={'work_order': work_order}, fields=['name', 'docstatus', 'status'], order_by='name')
	for x in jcs:
		try:
			jc = frappe.get_doc('Job Card', x.name)
			if jc.docstatus == 0 and (jc.status == 'Open' or jc.status == 'Material Transferred'):
				jc.append('time_logs',{
					'from_time': utils.add_to_date(utils.now_datetime(), days=-10),
					'to_time': utils.add_to_date(utils.add_to_date(utils.now_datetime(),minutes=10), days=-9),
					'completed_qty': 1})
				jc.save()
				jc.submit()
				frappe.db.commit()
			if jc.docstatus == 1  and jc.status == 'Work In Progress':
				frappe.db.sql("""update `tabJob Card` set status = 'Completed' where name = '{job_card}' and status = 'Work In Progress'""".format(job_card=jc.name))
				frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			traceback.print_exc()

def create_finishing_entry(work_order_number, se_date, se_time=None, se_series=None, se_name=None):
	work_order = frappe.get_doc("Work Order", work_order_number)
	from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_report
	columns, items = stock_balance_report({
		'from_date': utils.add_to_date(se_date, days=-10),
		'to_date': utils.add_to_date(se_date, days=-1),
		'warehouse': work_order.wip_warehouse})

	old_ns_value = -1;
	ste = frappe.new_doc('Stock Entry')

	if se_series is not None:
		ste.naming_series = se_series
	else:
		ste.naming_series = 'STE/20-21/'

	if se_name is not None:
		old_ns_value = frappe.db.sql("""select current from `tabSeries` where name = '{series}'""".format(series=ste.naming_series))[0][0]
		ns = frappe.get_doc('Naming Series')
		ns.prefix = ste.naming_series
		ns.current_value = int(se_name)-1
		ns.update_series_start()

	ste.set_posting_time = 1
	ste.posting_date = se_date
	ste.stock_entry_type = 'Manufacture'
	ste.work_order = work_order.name
	ste.from_bom = 1
	ste.fg_completed_qty = 1.0
	ste.append('items', {'item_code': work_order.production_item,
						't_warehouse': work_order.fg_warehouse,
						'qty': work_order.qty})
	for item in items:
		ste.append('items', {'item_code': item['item_code'],
							's_warehouse': work_order.wip_warehouse,
							'qty': item['bal_qty']})
	ste.insert()
	if old_ns_value > -1:
		ns = frappe.get_doc('Naming Series')
		ns.prefix = ste.naming_series
		ns.current_value = old_ns_value
		ns.update_series_start()

def update_work_order_item(work_order,new_item):
	frappe.db.sql("""update `tabWork Order` set production_item = '{item_code}' where name = '{work_order}'""".format(work_order=work_order, item_code=new_item))
	frappe.db.commit()

def clear_assembly_bay(bay_no):
	from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_report
	columns, items = stock_balance_report({
		'from_date': utils.add_to_date(utils.now_datetime(), days=-1),
		'to_date': utils.now_datetime(),
		'warehouse': bay_no})

	if len(items) > 0:
		ste = frappe.new_doc('Stock Entry')
		ste.naming_series = 'STE/20-21/'
		ste.stock_entry_type = 'Material Issue'
		for item in items:
			ste.append('items', {'item_code': item['item_code'],
								's_warehouse': bay_no,
								'qty': item['bal_qty']})
		ste.insert()
		ste.submit()
		frappe.db.commit()

def update_ste_expense_account(ste_no, account):
	try:
		ste = frappe.get_doc('Stock Entry', ste_no)
		if(ste.docstatus == 1):
			newste = copy.deepcopy(ste)
			newste.set_posting_time = 1
			newste.posting_date = ste.posting_date
			newste.posting_time = ste.posting_time
			for item in newste.items:
				item.expense_account = account
			ste_name = ste.name
			ste_name = ste.name.replace(ste.naming_series, '')
			ste_name = int(ste_name.split('-')[0])
			ste.cancel()
			ste.delete()
			old_ns_value = frappe.db.sql("""select current from `tabSeries` where name = '{series}'""".format(series=ste.naming_series))[0][0]
			ns = frappe.get_doc('Naming Series')
			ns.prefix = ste.naming_series
			ns.current_value = ste_name-1
			ns.update_series_start()
			newste.insert()
			ns.current_value = old_ns_value
			ns.update_series_start()
			frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		traceback.print_exc()

def fix_gst_valuation(purchase_invoice):
	ns = frappe.get_doc('Naming Series')
	pi = frappe.get_doc('Purchase Invoice', purchase_invoice)
	newpi = copy.deepcopy(pi)
	newpi.set_posting_time = 1
	newpi.posting_date = pi.posting_date
	newpi.posting_time = pi.posting_time
	pi.cancel()
	pi.delete()
	prec = frappe.get_doc('Purchase Receipt', pi.items[0].purchase_receipt)
	newprec = copy.deepcopy(prec)
	newprec.set_posting_time = 1
	newprec.posting_date = prec.posting_date
	newprec.posting_time = prec.posting_time
	prec.cancel()
	prec.delete()
	for taxrow in newprec.taxes:
		if("GST" in taxrow.account_head):
			taxrow.category = 'Total'
		elif("reight" in taxrow.account_head):
			taxrow.category = "Valuation and Total"
		else:
			taxrow.category = "Valuation and Total"
	ns.prefix = newprec.naming_series
	old_prec_ns_value = frappe.db.sql("""select current from `tabSeries` where name = '{series}'""".format(series=ns.prefix))[0][0]
	prec_name = newprec.name
	prec_name = prec_name.replace(ns.prefix, '')
	prec_name = int(prec_name.split('-')[0])
	ns.current_value = prec_name - 1
	ns.update_series_start()
	newprec.insert()
	for taxrow in newpi.taxes:
		if("GST" in taxrow.account_head):
			taxrow.category = 'Total'
		elif("reight" in taxrow.account_head):
			taxrow.category = "Valuation and Total"
		else:
			taxrow.category = "Valuation and Total"
	ns.prefix = newpi.naming_series
	old_pinv_ns_value = frappe.db.sql("""select current from `tabSeries` where name = '{series}'""".format(series=ns.prefix))[0][0]
	pinv_name = newpi.name
	pinv_name = pinv_name.replace(ns.prefix, '')
	pinv_name = int(pinv_name.split('-')[0])
	ns.current_value = pinv_name - 1
	ns.update_series_start()
	for item in newpi.items:
		index = 0
		for itemX in prec.items:
			if(itemX.name == item.pr_detail):
				break
			index = index+1
		item.pr_detail = newprec.items[index].name
	newpi.insert()
	ns.prefix = newprec.naming_series
	ns.current_value = old_prec_ns_value
	ns.update_series_start()
	ns.prefix = newpi.naming_series
	ns.current_value = old_pinv_ns_value
	ns.update_series_start()
	frappe.db.commit()
