import frappe
from frappe import _
from frappe.utils import escape_html
from frappe.website.utils import is_signup_disabled

@frappe.whitelist(allow_guest=True)
def sign_up(email: str, full_name: str, pwd: str, redirect_to:str) -> tuple[int, str]:
    if is_signup_disabled():
        frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))
    
    user = frappe.db.get("User", {"email": email})
    if user:
        if user.enabled:
            return 0,   ("Already Registered")
        else:
            return 0,   ("Registered but disabled")
    else:
        if frappe.db.get_creation_count("User", 60) > 300:
            frappe.respond_as_web_page(
                ("Temporarily Disabled"),
                (
                    "Too many users signed up recently, so the registration is disabled. Please try back in an hour"
                ),
                http_status_code=429,
            )
        
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": escape_html(full_name),
                "enabled": 0,
                "new_password": pwd,
                "user_type": "Website User",
                "send_welcome_email": 0
            }
        )
        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.insert()
        user.add_roles("Drive User")
        if redirect_to:
            frappe.cache.hset("redirect_after_login", user.name, redirect_to)
        doc_activate = frappe.new_doc('Drive Activate Account')
        doc_activate.email = email
        doc_activate.key = frappe.generate_hash(length=12)
        doc_activate.status = "Pending"
        doc_activate.email_sent_at = frappe.utils.now()
        doc_activate.save(ignore_permissions=True)
        send_email_welcome(full_name, email, pwd, doc_activate.key)
        return 1, _("Register account successfully. Please activate account to use")

def send_email_welcome(full_name, email, pwd, key_activate):
    activate_link = frappe.utils.get_url(f"/api/method/drive.api.activate_account?key={key_activate}")
    template = "activate_account"
    frappe.sendmail(
        recipients=email,
        subject=_("Welcome to RoadAI Drive"),
        template=template,
        args={"full_name": full_name, "email": email, "activate_link": activate_link},
        now=True
    )

@frappe.whitelist(allow_guest=True)
def login():
    frappe.local.login_manager.login()
