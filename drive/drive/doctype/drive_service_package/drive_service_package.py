# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import uuid


class DriveServicePackage(Document):
	def before_insert(self):
		self.code = str(uuid.uuid4().hex)
