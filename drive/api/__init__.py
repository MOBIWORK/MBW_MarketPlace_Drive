import frappe
from frappe.translate import get_all_translations

@frappe.whitelist(allow_guest=True)
def get_translations():
	if frappe.session.user != "Guest":
		language = frappe.db.get_value("User", frappe.session.user, "language")
	else:
		language = frappe.db.get_single_value("System Settings", "language")

	return get_all_translations(language)

@frappe.whitelist(allow_guest=True)
def activate_account(key: str = None):
	if not key:
		frappe.throw("Invalid or expired key")
	
	result = frappe.db.get_all("Drive Activate Account", filters={"key": key}, pluck="name")
	if not result:
		frappe.throw("Invalid or expired key")
	
	activate_account = frappe.get_doc("Drive Activate Account", result[0])
	if activate_account.status == "Accepted":
		frappe.local.login_manager.login_as(activate_account.email)
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/drive"
	else:
		activate_account.accept()
		activate_account.reload()
		if activate_account.status == "Accepted":
			frappe.local.login_manager.login_as(activate_account.email)
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = "/drive"