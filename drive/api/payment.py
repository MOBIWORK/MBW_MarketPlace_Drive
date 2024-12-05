import frappe
from payos import PayOS, ItemData, PaymentData

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
        doc_service_package = frappe.get_doc('Drive Service Package', doc_payment.code_package)
        historial_payment = {
            'name': doc_payment.name,
            'title': doc_service_package.title,
            'price': doc_payment.price,
            'status': doc_payment.status,
            'payment_time': doc_payment.payment_time
        }
        arr_historial_payments.append(historial_payment)
    
    return arr_historial_payments

@frappe.whitelist(methods=["POST"])
def create_paypment(name_package):
    client_id = frappe.db.get_single_value("Drive Instance Settings", "client_id_payos")
    api_key = frappe.db.get_single_value("Drive Instance Settings", "api_key_payos")
    checksum_key = frappe.db.get_single_value("Drive Instance Settings", "checksum_key_payos")
    payOS = PayOS(client_id=client_id, api_key=api_key, checksum_key=checksum_key)
    cancelUrl = frappe.utils.get_url("/drive")
    returnUrl = frappe.utils.get_url("/drive")
    doc_service_package = frappe.get_doc("Drive Service Package", name_package)
    doc_payment = frappe.new_doc("Drive Payment")
    doc_payment.form_of_payment = "Banking"
    doc_payment.code_package = name_package
    doc_payment.price = doc_service_package.unit_price
    doc_payment.status = "Outstanding"
    order_code = len(frappe.db.get_list('Drive Payment', pluck='name')) + 1
    doc_payment.order_code = order_code
    doc_payment.insert(ignore_permissions=True)
    paymentData = PaymentData(orderCode=order_code, amount=int(doc_service_package.unit_price), description=name_package,
     cancelUrl=cancelUrl, returnUrl=returnUrl)
    paymentLinkData = payOS.createPaymentLink(paymentData = paymentData)
    return paymentLinkData.checkoutUrl

@frappe.whitelist(methods=["POST"], allow_guest=True)
def callback_complete_payment(data):
    doc_test_ospayment = frappe.new_doc("Drive Test OSPayment")
    doc_test_ospayment.data_response = str(data)
    doc_test_ospayment.insert(ignore_permissions=True)
    if data.desc == "success" or data.desc == "Thành công":
        orderCode = data.orderCode
        doc_payment = frappe.get_doc("Drive Payment", {'order_code': orderCode})
        doc_payment.status = "Paid"
        doc_payment.save(ignore_permissions=True)
