import frappe

def after_insert_user(doc, method=None):
    doc_exist = frappe.db.exists("Drive Service Package Used", {"user": doc.name})
    if doc_exist is None:
        name_doc_service_package =  frappe.db.get_value("Drive Service Package", {"unit_price": 0}, ["name"])
        doc_service_package_used = frappe.new_doc('Drive Service Package Used')
        doc_service_package_used.user = doc.name
        doc_service_package_used.service_package = name_doc_service_package
        doc_service_package_used.insert(ignore_permissions=True)