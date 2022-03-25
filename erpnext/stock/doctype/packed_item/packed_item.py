# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt


import json

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from frappe.model.document import Document
from erpnext.controllers.buying_controller import BuyingController
from erpnext.controllers.selling_controller import SellingController
from erpnext.stock.get_item_details import get_item_details, get_price_list_rate


class PackedItem(Document):
	pass

def get_product_bundle_items(item_code):
	return frappe.db.sql("""select t1.item_code, t1.qty, t1.uom, t1.description, t1.weightage_per_qty
		from `tabProduct Bundle Item` t1, `tabProduct Bundle` t2
		where t2.new_item_code=%s and t1.parent = t2.name order by t1.idx""", item_code, as_dict=1)

def get_packing_item_details(item, company):
	return frappe.db.sql("""
		select i.item_name, i.is_stock_item, i.description, i.stock_uom, id.default_warehouse
		from `tabItem` i LEFT JOIN `tabItem Default` id ON id.parent=i.name and id.company=%s
		where i.name = %s""",
		(company, item), as_dict = 1)[0]

def get_bin_qty(item, warehouse):
	det = frappe.db.sql("""select actual_qty, projected_qty from `tabBin`
		where item_code = %s and warehouse = %s""", (item, warehouse), as_dict = 1)
	return det and det[0] or frappe._dict()

def get_item_supplier_code(item_code, supplier):
	return frappe.db.sql("""
		select i.supplier_part_no as supplier_code
		from `tabItem Supplier` i
		where i.parent = %s and i.supplier = %s""",
		(item_code, supplier), as_dict = 1)

def update_packing_list_item(doc, packing_item_code, qty, weightage_per_qty, main_item_row, description):
	if doc.amended_from:
		old_packed_items_map = get_old_packed_item_details(doc.packed_items)
	else:
		old_packed_items_map = False
	item = get_packing_item_details(packing_item_code, doc.company)

	# check if exists
	exists = 0
	for d in doc.get("packed_items"):
		if d.parent_item == main_item_row.item_code and d.item_code == packing_item_code:
			if d.parent_detail_docname != main_item_row.name:
				d.parent_detail_docname = main_item_row.name

			pi, exists = d, 1
			break

	if not exists:
		pi = doc.append('packed_items', {})

	pi.parent_item = main_item_row.item_code
	pi.item_code = packing_item_code
	pi.item_name = item.item_name
	pi.parent_detail_docname = main_item_row.name
	pi.uom = item.stock_uom
	pi.qty = flt(qty)
	pi.weightage_per_qty = flt(weightage_per_qty)
	if isinstance(doc, BuyingController):
		supplier_codes = get_item_supplier_code(pi.item_code, doc.supplier)
		if len(supplier_codes) > 0:
			pi.supplier_item_code = supplier_codes[0].supplier_code
	pi.conversion_factor = main_item_row.conversion_factor
	if description and not pi.description:
		pi.description = description
	if not pi.warehouse and not doc.amended_from:
		if isinstance(doc,SellingController):
			pi.warehouse = (main_item_row.warehouse if ((doc.get('is_pos')
				or not item.default_warehouse) and main_item_row.warehouse) else item.default_warehouse)
		elif isinstance(doc,BuyingController):
			pi.warehouse = (main_item_row.warehouse)
	if not pi.batch_no and not doc.amended_from:
		pi.batch_no = cstr(main_item_row.get("batch_no"))
	if not pi.target_warehouse:
		if isinstance(doc,SellingController):
			pi.target_warehouse = main_item_row.get("target_warehouse")
		elif isinstance(doc,BuyingController) and (not hasattr(doc,'is_return') or not doc.is_return):
			pi.target_warehouse = main_item_row.get("warehouse")
	bin = get_bin_qty(packing_item_code, pi.warehouse)
	pi.actual_qty = flt(bin.get("actual_qty"))
	pi.projected_qty = flt(bin.get("projected_qty"))
	if old_packed_items_map and old_packed_items_map.get((packing_item_code, main_item_row.item_code)):
		pi.batch_no = old_packed_items_map.get((packing_item_code, main_item_row.item_code))[0].batch_no
		pi.serial_no = old_packed_items_map.get((packing_item_code, main_item_row.item_code))[0].serial_no
		pi.warehouse = old_packed_items_map.get((packing_item_code, main_item_row.item_code))[0].warehouse

def make_packing_list(doc):
	"Make/Update packing list for Product Bundle Item."
	if doc.get("_action") and doc._action == "update_after_submit":
		return

	parent_items = []
	for d in doc.get("items"):
		if frappe.db.get_value("Product Bundle", {"new_item_code": d.item_code}):
			for i in get_product_bundle_items(d.item_code):
				update_packing_list_item(doc, i.item_code, flt(i.qty)*flt(d.stock_qty), i.weightage_per_qty, d, i.description)

			if [d.item_code, d.name] not in parent_items:
				parent_items.append([d.item_code, d.name])

	cleanup_packing_list(doc, parent_items)

	if frappe.db.get_single_value("Selling Settings", "editable_bundle_item_rates"):
		update_product_bundle_price(doc, parent_items)

def cleanup_packing_list(doc, parent_items):
	"""Remove all those child items which are no longer present in main item table"""
	delete_list = []
	for d in doc.get("packed_items"):
		if [d.parent_item, d.parent_detail_docname] not in parent_items:
			# mark for deletion from doclist
			delete_list.append(d)

	if not delete_list:
		return doc

	packed_items = doc.get("packed_items")
	doc.set("packed_items", [])

	for d in packed_items:
		if d not in delete_list:
			add_item_to_packing_list(doc, d)

def add_item_to_packing_list(doc, packed_item):
	doc.append("packed_items", {
		'parent_item': packed_item.parent_item,
		'item_code': packed_item.item_code,
		'item_name': packed_item.item_name,
		'uom': packed_item.uom,
		'qty': packed_item.qty,
		'rate': packed_item.rate,
		'conversion_factor': packed_item.conversion_factor,
		'description': packed_item.description,
		'warehouse': packed_item.warehouse,
		'batch_no': packed_item.batch_no,
		'actual_batch_qty': packed_item.actual_batch_qty,
		'serial_no': packed_item.serial_no,
		'target_warehouse': packed_item.target_warehouse,
		'actual_qty': packed_item.actual_qty,
		'projected_qty': packed_item.projected_qty,
		'incoming_rate': packed_item.incoming_rate,
		'prevdoc_doctype': packed_item.prevdoc_doctype,
		'parent_detail_docname': packed_item.parent_detail_docname
	})

	parent_items_price, reset = {}, False
	set_price_from_children = frappe.db.get_single_value("Selling Settings", "editable_bundle_item_rates")

	stale_packed_items_table = get_indexed_packed_items_table(doc)

	reset = reset_packing_list(doc)

	for item_row in doc.get("items"):
		if frappe.db.exists("Product Bundle", {"new_item_code": item_row.item_code}):
			for bundle_item in get_product_bundle_items(item_row.item_code):
				pi_row = add_packed_item_row(
					doc=doc, packing_item=bundle_item,
					main_item_row=item_row, packed_items_table=stale_packed_items_table,
					reset=reset
				)
				item_data = get_packed_item_details(bundle_item.item_code, doc.company)
				update_packed_item_basic_data(item_row, pi_row, bundle_item, item_data)
				update_packed_item_stock_data(item_row, pi_row, bundle_item, item_data, doc)
				update_packed_item_price_data(pi_row, item_data, doc)
				update_packed_item_from_cancelled_doc(item_row, bundle_item, pi_row, doc)

				if set_price_from_children: # create/update bundle item wise price dict
					update_product_bundle_rate(parent_items_price, pi_row)

	if parent_items_price:
		set_product_bundle_rate_amount(doc, parent_items_price) # set price in bundle item

def get_indexed_packed_items_table(doc):
	"""
		Create dict from stale packed items table like:
		{(Parent Item 1, Bundle Item 1, ae4b5678): {...}, (key): {value}}

		Use: to quickly retrieve/check if row existed in table instead of looping n times
	"""
	indexed_table = {}
	for packed_item in doc.get("packed_items"):
		key = (packed_item.parent_item, packed_item.item_code, packed_item.parent_detail_docname)
		indexed_table[key] = packed_item

	return indexed_table

def reset_packing_list(doc):
	"Conditionally reset the table and return if it was reset or not."
	reset_table = False
	doc_before_save = doc.get_doc_before_save()

	if doc_before_save:
		# reset table if:
		# 1. items were deleted
		# 2. if bundle item replaced by another item (same no. of items but different items)
		# we maintain list to track recurring item rows as well
		items_before_save = [item.item_code for item in doc_before_save.get("items")]
		items_after_save = [item.item_code for item in doc.get("items")]
		reset_table = items_before_save != items_after_save
	else:
		# reset: if via Update Items OR
		# if new mapped doc with packed items set (SO -> DN)
		# (cannot determine action)
		reset_table = True

	if reset_table:
		doc.set("packed_items", [])
	return reset_table

def get_product_bundle_items(item_code):
	product_bundle = frappe.qb.DocType("Product Bundle")
	product_bundle_item = frappe.qb.DocType("Product Bundle Item")

	query = (
		frappe.qb.from_(product_bundle_item)
		.join(product_bundle).on(product_bundle_item.parent == product_bundle.name)
		.select(
			product_bundle_item.item_code,
			product_bundle_item.qty,
			product_bundle_item.uom,
			product_bundle_item.description
		).where(
			product_bundle.new_item_code == item_code
		).orderby(
			product_bundle_item.idx
		)
	)
	return query.run(as_dict=True)

def add_packed_item_row(doc, packing_item, main_item_row, packed_items_table, reset):
	"""Add and return packed item row.
		doc: Transaction document
		packing_item (dict): Packed Item details
		main_item_row (dict): Items table row corresponding to packed item
		packed_items_table (dict): Packed Items table before save (indexed)
		reset (bool): State if table is reset or preserved as is
	"""
	exists, pi_row = False, {}

	# check if row already exists in packed items table
	key = (main_item_row.item_code, packing_item.item_code, main_item_row.name)
	if packed_items_table.get(key):
		pi_row, exists = packed_items_table.get(key), True

	if not exists:
		pi_row = doc.append('packed_items', {})
	elif reset: # add row if row exists but table is reset
		pi_row.idx, pi_row.name = None, None
		pi_row = doc.append('packed_items', pi_row)

	return pi_row

def get_packed_item_details(item_code, company):
	item = frappe.qb.DocType("Item")
	item_default = frappe.qb.DocType("Item Default")
	query = (
		frappe.qb.from_(item)
		.left_join(item_default)
		.on(
			(item_default.parent == item.name)
			& (item_default.company == company)
		).select(
			item.item_name, item.is_stock_item,
			item.description, item.stock_uom,
			item.valuation_rate,
			item_default.default_warehouse
		).where(
			item.name == item_code
		)
	)
	return query.run(as_dict=True)[0]

def update_packed_item_basic_data(main_item_row, pi_row, packing_item, item_data):
	pi_row.parent_item = main_item_row.item_code
	pi_row.parent_detail_docname = main_item_row.name
	pi_row.item_code = packing_item.item_code
	pi_row.item_name = item_data.item_name
	pi_row.uom = item_data.stock_uom
	pi_row.qty = flt(packing_item.qty) * flt(main_item_row.stock_qty)
	pi_row.conversion_factor = main_item_row.conversion_factor

	if not pi_row.description:
		pi_row.description = packing_item.get("description")

def update_packed_item_stock_data(main_item_row, pi_row, packing_item, item_data, doc):
	# TODO batch_no, actual_batch_qty, incoming_rate
	if not pi_row.warehouse and not doc.amended_from:
		fetch_warehouse = (doc.get('is_pos') or item_data.is_stock_item or not item_data.default_warehouse)
		pi_row.warehouse = (main_item_row.warehouse if (fetch_warehouse and main_item_row.warehouse)
			else item_data.default_warehouse)

	if not pi_row.target_warehouse:
		pi_row.target_warehouse = main_item_row.get("target_warehouse")

	bin = get_packed_item_bin_qty(packing_item.item_code, pi_row.warehouse)
	pi_row.actual_qty = flt(bin.get("actual_qty"))
	pi_row.projected_qty = flt(bin.get("projected_qty"))

def update_packed_item_price_data(pi_row, item_data, doc):
	"Set price as per price list or from the Item master."
	if pi_row.rate:
		return

	item_doc = frappe.get_cached_doc("Item", pi_row.item_code)
	row_data = pi_row.as_dict().copy()
	row_data.update({
		"company": doc.get("company"),
		"price_list": doc.get("selling_price_list"),
		"currency": doc.get("currency"),
		"conversion_rate": doc.get("conversion_rate"),
	})
	rate = get_price_list_rate(row_data, item_doc).get("price_list_rate")

	pi_row.rate = rate or item_data.get("valuation_rate") or 0.0

def update_packed_item_from_cancelled_doc(main_item_row, packing_item, pi_row, doc):
	"Update packed item row details from cancelled doc into amended doc."
	prev_doc_packed_items_map = None
	if doc.amended_from:
		prev_doc_packed_items_map = get_cancelled_doc_packed_item_details(doc.packed_items)

	if prev_doc_packed_items_map and prev_doc_packed_items_map.get((packing_item.item_code, main_item_row.item_code)):
		prev_doc_row = prev_doc_packed_items_map.get((packing_item.item_code, main_item_row.item_code))
		pi_row.batch_no = prev_doc_row[0].batch_no
		pi_row.serial_no = prev_doc_row[0].serial_no
		pi_row.warehouse = prev_doc_row[0].warehouse

def get_packed_item_bin_qty(item, warehouse):
	bin_data = frappe.db.get_values(
		"Bin",
		fieldname=["actual_qty", "projected_qty"],
		filters={"item_code": item, "warehouse": warehouse},
		as_dict=True
	)

	return bin_data[0] if bin_data else {}

def get_cancelled_doc_packed_item_details(old_packed_items):
	prev_doc_packed_items_map = {}
	for items in old_packed_items:
		prev_doc_packed_items_map.setdefault((items.item_code ,items.parent_item), []).append(items.as_dict())
	return prev_doc_packed_items_map

def update_product_bundle_rate(parent_items_price, pi_row):
	"""
		Update the price dict of Product Bundles based on the rates of the Items in the bundle.

		Stucture:
		{(Bundle Item 1, ae56fgji): 150.0, (Bundle Item 2, bc78fkjo): 200.0}
	"""
	key = (pi_row.parent_item, pi_row.parent_detail_docname)
	rate = parent_items_price.get(key)
	if not rate:
		parent_items_price[key] = 0.0

	parent_items_price[key] += flt(pi_row.rate)

def set_product_bundle_rate_amount(doc, parent_items_price):
	"Set cumulative rate and amount in bundle item."
	for item in doc.get("items"):
		bundle_rate = parent_items_price.get((item.item_code, item.name))
		if bundle_rate and bundle_rate != item.rate:
			item.rate = bundle_rate
			item.amount = flt(bundle_rate * item.qty)

def on_doctype_update():
	frappe.db.add_index("Packed Item", ["item_code", "warehouse"])


@frappe.whitelist()
def get_items_from_product_bundle(row):
	row, items = json.loads(row), []

	bundled_items = get_product_bundle_items(row["item_code"])
	for item in bundled_items:
		row.update({
			"item_code": item.item_code,
			"qty": flt(row["quantity"]) * flt(item.qty)
		})
		items.append(get_item_details(row))

	return items
