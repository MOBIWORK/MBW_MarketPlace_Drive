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