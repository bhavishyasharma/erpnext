# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CompetitorModel(Document):
	def validate(self):
		self.update_injection_unit_parameters()
		self.update_clamping_unit_parameters()

	def update_injection_unit_parameters(self):
		injection_capacity_para = frappe.get_doc("Competitor Model Injection Unit Parameter", "Injection Capacity")
		injection_capacity_gpps_para = frappe.get_doc("Competitor Model Injection Unit Parameter", "Injection Capacity (GPPS)")
		injection_rate_para = frappe.get_doc("Competitor Model Injection Unit Parameter", "Injection Rate")
		injection_rate_gpps_para = frappe.get_doc("Competitor Model Injection Unit Parameter", "Injection Rate (GPPS)")
		iup_icp_index = -1
		iup_icgp_index = -1
		iup_irp_index = -1
		iup_irgp_index = -1
		index = 0
		for iup in self.injection_unit_parameters:
			if iup.p_index == injection_capacity_para.p_index:
				iup_icp_index = index
			elif iup.p_index == injection_capacity_gpps_para.p_index:
				iup_icgp_index = index
			elif iup.p_index == injection_rate_para.p_index:
				iup_irp_index = index
			elif iup.p_index == injection_rate_gpps_para.p_index:
				iup_irgp_index = index
			index = index+1
		if iup_icp_index!=-1 and iup_icgp_index==-1:
			row = self.append('injection_unit_parameters', {})
			row.parameter_name = injection_capacity_gpps_para.name
			row.unit = injection_capacity_gpps_para.unit
			row.p_index = injection_capacity_gpps_para.p_index
			row.a_ = flt(flt(self.injection_unit_parameters[iup_icp_index].a_) * 0.91,2)
			row.a = flt(flt(self.injection_unit_parameters[iup_icp_index].a) * 0.91,2)
			row.b = flt(flt(self.injection_unit_parameters[iup_icp_index].b) * 0.91,2)
			row.c = flt(flt(self.injection_unit_parameters[iup_icp_index].c) * 0.91,2)
			row.d = flt(flt(self.injection_unit_parameters[iup_icp_index].d) * 0.91,2)
			if row.a_==0.0:
				row.a_=None
			if row.a == 0.0:
				row.a = None
			if row.c == 0.0:
				row.c = None
			if row.d == 0.0:
				row.d = None
		elif iup_icgp_index!=-1 and iup_icp_index==-1:
			row = self.append('injection_unit_parameters', {})
			row.parameter_name = injection_capacity_para.name
			row.unit = injection_capacity_para.unit
			row.p_index = injection_capacity_para.p_index
			row.a_ = flt(flt(self.injection_unit_parameters[iup_icgp_index].a_) / 0.91,2)
			row.a = flt(flt(self.injection_unit_parameters[iup_icgp_index].a) / 0.91,2)
			row.b = flt(flt(self.injection_unit_parameters[iup_icgp_index].b) / 0.9,2)
			row.c = flt(flt(self.injection_unit_parameters[iup_icgp_index].c) / 0.91,2)
			row.d = flt(flt(self.injection_unit_parameters[iup_icgp_index].d) / 0.91,2)
			if row.a_==0.0:
				row.a_ = None
			if row.a==0.0:
				row.a = None
			if row.c==0.0:
				row.c = None
			if row.d==0.0:
				row.d = None
		if iup_irp_index!=-1 and iup_irgp_index==-1:
			row = self.append('injection_unit_parameters', {})
			row.parameter_name = injection_rate_gpps_para.name
			row.unit = injection_rate_gpps_para.unit
			row.p_index = injection_rate_gpps_para.p_index
			row.a_ = flt(flt(self.injection_unit_parameters[iup_irp_index].a_) * 0.91,2)
			row.a = flt(flt(self.injection_unit_parameters[iup_irp_index].a) * 0.91,2)
			row.b = flt(flt(self.injection_unit_parameters[iup_irp_index].b) * 0.91,2)
			row.c = flt(flt(self.injection_unit_parameters[iup_irp_index].c) * 0.91,2)
			row.d = flt(flt(self.injection_unit_parameters[iup_irp_index].d) * 0.91,2)
			if row.a_ == 0.0:
				row.a_ = None
			if row.a == 0.0:
				row.a = None
			if row.c == 0.0:
				row.c = None
			if row.d == 0.0:
				row.d = None
		elif iup_irgp_index!=-1 and iup_irp_index==-1:
			row = self.append('injection_unit_parameters', {})
			row.parameter_name = injection_rate_para.name
			row.unit = injection_rate_para.unit
			row.p_index = injection_rate_para.p_index
			row.a_ = flt(flt(self.injection_unit_parameters[iup_irgp_index].a_) / 0.91,2)
			row.a = flt(flt(self.injection_unit_parameters[iup_irgp_index].a) / 0.91,2)
			row.b = flt(flt(self.injection_unit_parameters[iup_irgp_index].b) / 0.91,2)
			row.c = flt(flt(self.injection_unit_parameters[iup_irgp_index].c) / 0.91,2)
			row.d = flt(flt(self.injection_unit_parameters[iup_irgp_index].d) / 0.91,2)
			if row.a_ == 0.0:
				row.a_ = None
			if row.a == 0.0:
				row.a = None
			if row.c == 0.0:
				row.c = None
			if row.d == 0.0:
				row.d = None

	def update_clamping_unit_parameters(self):
		max_daylight_para = frappe.get_doc("Competitor Model Clamping Unit Parameter", "Max Daylight")
		max_mould_height_para = frappe.get_doc("Competitor Model Clamping Unit Parameter", "Max Mould Height")
		opening_stroke_para = frappe.get_doc("Competitor Model Clamping Unit Parameter", "Opening Stroke")
		cup_mdp_index = -1
		cup_mmhp_index = -1
		cup_osp_index = -1
		index = 0
		for cup in self.clamping_unit_parameters:
			if cup.p_index == max_daylight_para.p_index:
				cup_mdp_index = index
			elif cup.p_index == max_mould_height_para.p_index:
				cup_mmhp_index = index
			elif cup.p_index == opening_stroke_para.p_index:
				cup_osp_index = index
			index = index + 1
		if cup_osp_index!=-1 and cup_mmhp_index!=-1 and cup_mdp_index==-1:
			row = self.append('clamping_unit_parameters', {})
			row.parameter_name = max_daylight_para.name
			row.unit = max_daylight_para.unit
			row.p_index = max_daylight_para.p_index
			row.standard = flt(flt(self.clamping_unit_parameters[cup_osp_index].standard) + flt(self.clamping_unit_parameters[cup_mmhp_index].standard),2)
			row.optional = flt(flt(self.clamping_unit_parameters[cup_osp_index].optional) + flt(self.clamping_unit_parameters[cup_mmhp_index].optional),2)
			if row.optional == 0.0:
				row.optional = None
