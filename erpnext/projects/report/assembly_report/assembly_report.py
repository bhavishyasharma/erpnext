# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	projects = frappe.get_list('Project',
		filters={
			'status': 'Open'
    		},
		fields=['project_name','status'],
		as_list=True,
		order_by='project_name'
	)
	taskNames = frappe.db.sql("""select distinct(subject)
		from `tabProject Template Task`
		where subject not like "%Procurement%"
		and subject not like "%Processing%"
		and subject not like "%Segregation%"
		order by idx
	""")
	columns.append({
		"fieldname": "task",
		"label": _("Task"),
		"width": 300
	})
	counter = 0
	for project in projects:
		columns.append({
			"fieldname": "project_"+str(counter),
			"label": project[0]
		})
		counter = counter + 1
	counter = 0
	for taskName in taskNames:
		row = [taskName[0]]
		for project in projects:
			task = frappe.get_list('Task',
				filters={
					'project': project[0],
					'subject': taskName[0]
				},
				fields=['subject','status','exp_end_date','act_end_date']
			)
			if task and len(task)>0:
				row.append({ 'status': task[0]['status'],
					'end_date': task[0]['exp_end_date'],
					'act_end_date': task[0]['act_end_date']})
			else:
				row.append({})
		counter = counter + 1
		data.append(row)
	return columns, data
