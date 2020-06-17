import frappe
from frappe.utils import nowdate

@frappe.whitelist(allow_guest=True)
def submit_query(subject, product, service, name, company, email, phone, query):
	lead = frappe.db.get_list('Lead',filters={'email_id': email}, fields=['name'])
	print(lead)
	exists = False
	if len(lead)>0:
		lead= frappe.get_doc('Lead', lead[0]['name'])
		exists = True
	else:
		lead = frappe.new_doc('Lead')
		lead.lead_name = name
		lead.company_name = company
		lead.email_id = email
		lead.phone = phone
		lead.source = "Website"
	if exists:
		if subject == "General":
			lead.notes = lead.notes + "<br>" + str(nowdate()) + ":" + query
		elif subject == "Product Query":
			lead.notes = lead.notes + "<br>" + str(nowdate()) + ":" + "Subject: " +subject + "<br>Product: " + product + "<br>Query: " + query
		else:
			lead.notes = lead.notes + "<br>" + str(nowdate()) + ":" + "Subject: "+subject+"<br>Service: "+service+"<br>Query: "+ query
		lead.save(ignore_permissions=True)
	else:
		if subject == "General":
			lead.notes = query
		elif subject == "Product Query":
			lead.notes = "Subject: " +subject + "<br>Product: " + product + "<br>Query: " + query
		else:
			lead.notes = "Subject: "+subject+"<br>Service: "+service+"<br>Query: "+query
		lead.insert(ignore_permissions=True)
	return True
