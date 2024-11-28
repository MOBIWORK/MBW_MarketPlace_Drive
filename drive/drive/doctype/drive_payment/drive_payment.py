# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class DrivePayment(Document):
	def on_update(self):
		if self.status == "Paid":
			doc_service_package_used = frappe.get_doc({
				'doctype': 'Drive Service Package Used',
				'user': frappe.session.user
			})
			doc_service_package_used.service_package = self.code_package
			doc_service_package_used.save(ignore_permissions=True)
