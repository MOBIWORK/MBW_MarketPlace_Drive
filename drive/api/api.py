import frappe
from frappe.utils import validate_email_address, split_emails
import requests
import xml.etree.ElementTree as ET
import gpxpy
import gpxpy.gpx
from datetime import datetime
import shutil

@frappe.whitelist(allow_guest=True)
def oauth_providers():
    from frappe.utils.html_utils import get_icon_html
    from frappe.utils.password import get_decrypted_password
    from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys

    out = []
    providers = frappe.get_all(
        "Social Login Key",
        filters={"enable_social_login": 1},
        fields=["name", "client_id", "base_url", "provider_name", "icon"],
        order_by="name",
    )

    for provider in providers:
        client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
        if not client_secret:
            continue

        icon = None
        if provider.icon:
            if provider.provider_name == "Custom":
                icon = get_icon_html(provider.icon, small=True)
            else:
                icon = f"<img src='{provider.icon}' alt={provider.provider_name}>"

        if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
            out.append(
                {
                    "name": provider.name,
                    "provider_name": provider.provider_name,
                    "auth_url": get_oauth2_authorize_url(provider.name, "/drive/home"),
                    "icon": icon,
                }
            )
    return out

@frappe.whitelist(allow_guest=True)
def get_server_timezone():
    return frappe.db.get_single_value('System Settings', 'time_zone')

@frappe.whitelist()
def get_setting_api():
    doc_setting = frappe.get_single('Drive Instance Settings')
    api_key_map = doc_setting.api_key_map
    client_id_qrcode = doc_setting.client_id
    api_key_qrcode = doc_setting.api_key
    code_bank = doc_setting.code_bank
    name_bank = doc_setting.name_bank
    account_name_banking = doc_setting.account_name_banking
    account_number_banking = doc_setting.account_number_banking
    return {
        'api_key_map': api_key_map,
        'client_id_qrcode': client_id_qrcode,
        'api_key_qrcode': api_key_qrcode,
        'code_bank': code_bank,
        'name_bank': name_bank,
        'account_name_banking': account_name_banking,
        'account_number_banking': account_number_banking
    }

@frappe.whitelist()
def test_get_content_gpx():
    # Gọi API để lấy nội dung
    url = "https://eov-test.mbwnext.com/api/method/drive.api.files.get_file_content?entity_name=1ca177ee456e4d9c912e39b65df98444"
    response = requests.get(url, stream=True, timeout=300)
    with open("geotesst.gpx", "wb") as file:
        shutil.copyfileobj(response.raw, file)

    with open("geotesst.gpx", "r") as file:
        print("80 ", file)   
    print("Dữ liệu GPX đã được ghi vào file: test_output.gpx")