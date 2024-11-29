# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from datetime import datetime

class DrivePayment(Document):
	def before_insert(self):
		if self.price == 0:
			self.status = "Paid"
			self.payment_time = datetime.now()

	def on_update(self):
		if self.status == "Paid":
			doc_service_package_used = frappe.get_doc({
				'doctype': 'Drive Service Package Used',
				'user': frappe.session.user
			})
			doc_service_package_used.service_package = self.code_package
			doc_service_package_used.save(ignore_permissions=True)
			frappe.publish_realtime('event_reset_package_used')
