import frappe

@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_data_payment(data):
    doc_test_ospayment = frappe.new_doc("Drive Test OSPayment")
    doc_test_ospayment.data_response = str(data)
    doc_test_ospayment.insert(ignore_permissions=True)

@frappe.whitelist(methods=["POST"], allow_guest=True)
def cancel_payment(data):
    doc_test_ospayment = frappe.new_doc("Drive Test OSPayment")
    doc_test_ospayment.data_response = str(data)
    doc_test_ospayment.insert(ignore_permissions=True)