# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class CompetitionComparison(Document):
	pass

def get_screws(injection_unit_parameters):
	screws = []
	for i in injection_unit_parameters:
		if 'A+' not in screws and i.a_ is not None and i.a_ != "":
			screws.append('A+')
		if 'A' not in screws and i.a is not None and i.a != "":
			screws.append('A')
		if 'B' not in screws and i.b is not None and i.b != "":
			screws.append('B')
		if 'C' not in screws and i.c is not None and i.c != "":
			screws.append('C')
		if 'D' not in screws and i.d is not None and i.d != "":
			screws.append('D')
	screws.sort()
	return screws

def get_parameter_index(parameters, p_index):
	index = 0
	for para in parameters:
		if para.p_index == p_index:
			return index
		index = index + 1
	return -1

@frappe.whitelist()
def get_comparison(models):
	columns = [
		{
			"name": "parameter",
			"label": "Parameter",
			"span": 1,
			"align": "left"
		},
		{
			"name": "unit",
			"label": "Unit",
			"span": 1,
			"align": "left"
		}
	]
	rows = [
		{
			"key": "injection_unit_international_size",
			"parameter": "Injection Unit",
			"unit": "",
			"className": "font-weight-bold",
			"empty": False,
			"from_model": True,
			"data": []
		},
		{
			"key": "screw",
			"parameter": "Screw",
			"unit": "",
			"className": "",
			"empty": False,
			"from_model": False,
			"data": []
		}
	]
	iu_parameters = frappe.get_list(doctype="Competitor Model Injection Unit Parameter", filters={}, fields=['name', 'unit', 'p_index'], order_by='p_index')
	for iup in iu_parameters:
		rows.append({
			"key": 'iu_'+str(iup['p_index']),
			"parameter": iup['name'],
			"unit":  iup['unit'],
			"className": "",
			"empty": False,
			"from_model": False,
			"data": []
		})
	rows.append({
		"key": "screw_stroke",
		"parameter": "Screw Stroke",
		"unit": "MM",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "screw_speed",
		"parameter": "Screw Speed",
		"unit": "RPM",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "nozzle_force",
		"parameter": "Nozzle Force",
		"unitName": "kN",
		"class": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "nozzle_protrusion",
		"parameter": "Nozzle Protrusion",
		"unit": "MM",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": 'clamping_unit_international_size',
		"parameter": "Clamping Unit Size",
		"unit": "",
		"className": "font-weight-bold",
		"empty": False,
		"from_model": True,
		"data": []
	})
	cu_parameters = frappe.get_list(doctype="Competitor Model Clamping Unit Parameter", filters={}, fields=['name', 'unit', 'p_index'], order_by='p_index')
	for cup in cu_parameters:
		rows.append({
			"key": 'cu_'+str(cup['p_index']),
			"parameter": cup['name'],
			"unit": cup['unit'],
			"className": "",
			"empty": False,
			"from_model": False,
			"data": []
		})
	rows.append({
		"key": "other_details",
		"parameter": "Other Details",
		"unit": "",
		"className": "font-weight-bold",
		"empty": True,
		"from_model": False,
		"data": []
	})
	rows.append({
		"key": "motor_load",
		"parameter": "Motor Load",
		"unit": "kW",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "heating_load",
		"parameter": "Heating Load",
		"unit": "kW",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "heating_zones",
		"parameter": "Heating Zones",
		"unit": "Nos",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "dimensions",
		"parameter": "Dimensions",
		"unit": "Meter LxBxH",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "oil_tank_capacity",
		"parameter": "Oil Tank Capacity",
		"unit": "Litres",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	rows.append({
		"key": "hopper_capacity",
		"parameter": "Hopper Capacity",
		"unit": "kg",
		"className": "",
		"empty": False,
		"from_model": True,
		"data":  []
	})
	rows.append({
		"key": "machine_weight",
		"parameter": "Machine Weight",
		"unit": "Ton",
		"className": "",
		"empty": False,
		"from_model": True,
		"data": []
	})
	model_list = json.loads(models)
	model_index = 0
	for model_name in model_list:
		model = frappe.get_doc("Competitor Model", model_name)
		screws = get_screws(model.injection_unit_parameters)
		columns.append({
			"name": model_name,
			"label": model_name,
			"span": len(screws),
			"align": "center"
		})
		for r in rows:
			if r["empty"]:
				r["data"].append({ "value": " ", "span": len(screws) })
			elif r["from_model"]:
				r["data"].append({ "value": model.get(r["key"]), "span": len(screws) })
			elif r["key"] == "screw":
				for s in screws:
					r["data"].append({
						"value": s,
						"span": 1
					})
			elif r["key"].startswith('iu_'):
				index = get_parameter_index(model.injection_unit_parameters, int(r["key"].split('iu_')[1]))
				if index < 0:
					r["data"].append({ "value": " ", "span": len(screws) })
				else:
					if 'A+' in screws:
						r["data"].append({
							"value": model.injection_unit_parameters[index].a_,
							"span": 1
						})
					if 'A' in screws:
						r["data"].append({
							"value": model.injection_unit_parameters[index].a,
							"span": 1
						})
					if 'B' in screws:
						r["data"].append({
							"value": model.injection_unit_parameters[index].b,
							"span": 1
						})
					if 'C' in screws:
						r["data"].append({
							"value": model.injection_unit_parameters[index].c,
							"span": 1
						})
					if 'D' in screws:
						r["data"].append({
							"value": model.injection_unit_parameters[index].d,
							"span": 1
						})
			elif r["key"].startswith('cu_'):
				index = get_parameter_index(model.clamping_unit_parameters, int(r["key"].split('cu_')[1]))
				if index < 0:
					r["data"].append({ "value": " ", "span": len(screws) })
				else:
					r["data"].append({
						"value": model.clamping_unit_parameters[index].standard,
						"optional": model.clamping_unit_parameters[index].optional,
						"span": len(screws)
					})

	return { "columns": columns, "rows": rows }
