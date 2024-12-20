# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe


class DriveActivateAccount(Document):
	def accept(self):
		if self.status == "Expired":
			frappe.throw("Invalid or expired key")
		
		self.status = "Accepted"
		self.accepted_at = frappe.utils.now()
		self.save(ignore_permissions=True)
		self.update_status_user()
	
	def update_status_user(self):
		user = frappe.get_doc("User", self.email)
		user.enabled = 1
		user.save(ignore_permissions=True)

def expire_activates():
	"""expire activate after 3 days"""
	from frappe.utils import add_days, now

	days = 3
	activates_to_expire = frappe.db.get_all(
		"Drive Activate Account", filters={"status": "Pending", "creation": ["<", add_days(now(), -days)]}
	)
	for activate in activates_to_expire:
		activate = frappe.get_doc("Drive Activate Account", activate.name)
		activate.status = "Expired"
		activate.save(ignore_permissions=True)
