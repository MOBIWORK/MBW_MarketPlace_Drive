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
                "enabled": 1,
                "new_password": pwd,
                "user_type": "Website User"
            }
        )
        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.insert()
        user.add_roles("Drive User")
        if redirect_to:
            frappe.cache.hset("redirect_after_login", user.name, redirect_to)
        
        if user.flags.email_sent:
            return 1, _("Register account successfully")
        else:
            return 2, _("Please ask your administrator to verify your sign-up")
            
