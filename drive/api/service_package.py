import frappe

@frappe.whitelist()
def list_package():
    docs_package = frappe.get_list('Drive Service Package',
        filters={
            'show': True
        },
        fields=['title', 'code', 'storage_volume', 'pupv', 'unit_price'],
        order_by='creation asc'
    )
    return docs_package

@frappe.whitelist()
def package_used():
    package_code_used = ""
    doc_package_used = frappe.db.get("Drive Service Package Used", {"user": frappe.session.user})
    if doc_package_used:
        package_code_used = doc_package_used.service_package
    else:
        name, code =  frappe.db.get_value("Drive Service Package", {"unit_price": 0}, ["name", "code"])
        doc_service_package_used = frappe.new_doc('Drive Service Package Used')
        doc_service_package_used.user = frappe.session.user
        doc_service_package_used.service_package = name
        doc_service_package_used.insert(ignore_permissions=True)
        package_code_used = code
    return package_code_used