import frappe

@frappe.whitelist()
def historial_payments():
    arr_historial_payments = []
    doc_payments = frappe.db.get_list('Drive Payment',
        filters={
            'owner': frappe.session.user
        },
        fields=['name', 'code_package', 'price', 'status', 'payment_time']
    )
    for doc_payment in doc_payments:
        doc_service_package = frappe.get_doc('Drive Service Package', {'code': doc_payment.code_package})
        historial_payment = {
            'name': doc_payment.name,
            'title': doc_service_package.title,
            'price': doc_payment.price,
            'status': doc_payment.status,
            'payment_time': doc_payment.payment_time
        }
        arr_historial_payments.append(historial_payment)
    
    return arr_historial_payments