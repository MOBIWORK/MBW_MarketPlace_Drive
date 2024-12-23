# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from drive.api.storage import add_new_site_config_key
from drive.utils.s3 import get_connect_s3, create_bucket_with_connect
from payos import PayOS

class DriveInstanceSettings(Document):
    def before_save(self):
        add_new_site_config_key("max_storage", self.self_storage_limit)
    
    @frappe.whitelist()
    def create_bucket(self):
        doc_setting = frappe.get_single('Drive Instance Settings')
        aws_endpoint_url = doc_setting.aws_end_point
        aws_access_key = doc_setting.aws_access_key
        aws_secret_access_key = doc_setting.get_password('aws_secret_key')
        connect_s3 = get_connect_s3(aws_endpoint_url, aws_access_key, aws_secret_access_key)
        create_bucket_with_connect(connect_s3)
    
    @frappe.whitelist()
    def create_confirm_webhook_payos(self):
        client_id = frappe.db.get_single_value("Drive Instance Settings", "client_id_payos")
        api_key = frappe.db.get_single_value("Drive Instance Settings", "api_key_payos")
        checksum_key = frappe.db.get_single_value("Drive Instance Settings", "checksum_key_payos")
        payOS = PayOS(client_id=client_id, api_key=api_key, checksum_key=checksum_key)
        payOS.confirmWebhook(frappe.utils.get_url("/api/method/drive.api.payment.callback_complete_payment"))

