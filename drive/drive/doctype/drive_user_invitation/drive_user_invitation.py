# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.document import Document
from frappe.utils import (
    add_days,
    get_datetime,
    now,
    validate_email_address,
)
from drive.api.language import get_language

EXPIRY_DAYS = 1


class DriveUserInvitation(Document):
    def has_expired(self):
        return get_datetime(self.creation) < get_datetime(add_days(now(), -EXPIRY_DAYS))

    def before_insert(self):
        validate_email_address(self.email, True)

    def after_insert(self):
        self.invite_via_email()

    def invite_via_email(self):
        lang = get_language()
        lang = lang if lang in ['vi', 'en'] else 'vi'

        title = 'Frappe Drive'
        subject = _("{0} - Invitation").format(title)
        template = f"{lang}_" + "drive_invitation"

        frappe.sendmail(
            recipients=self.email,
            subject=subject,
            template=template,
            args={
                "invite_link": frappe.utils.get_url(
                    f"/api/method/drive.utils.users.accept_invitation?key={self.name}"
                ),
                "user": frappe.session.user,
                "team_name": frappe.db.get_value("Drive Team", self.team, "title"),
            },
            now=True,
        )

    def accept(self):
        if self.status == "Expired" or self.has_expired():
            self.status = "Expired"
            self.save(ignore_permissions=True)
            frappe.throw("Invalid or expired key")

        frappe.local.response["type"] = "redirect"
        if not frappe.db.exists("User", self.email):
            frappe.local.response["location"] = (
                f"/login?email={self.email}&invite={frappe.db.get_value('Drive Team', self.team, 'title')}#signup"
            )
            return
        team = frappe.get_doc("Drive Team", self.team)
        team.append("users", {"user": self.email})
        team.save(ignore_permissions=True)
        self.status = "Accepted"
        self.accepted_at = frappe.utils.now()
        self.save(ignore_permissions=True)
        frappe.local.login_manager.login_as(self.email)
        frappe.local.response["location"] = "/drive/" + self.team
