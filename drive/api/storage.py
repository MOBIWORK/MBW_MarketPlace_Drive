import frappe
from pathlib import Path
from pypika import functions as fn
import os
import json


@frappe.whitelist()
def get_max_storage():
    """
    Retrieves the maximum storage limit for the user's package used.
    The storage limit is returned in bytes, with a block size of 1024.

    Returns:
        int: The maximum storage limit in bytes.
    """
    doc_package_used = frappe.db.get("Drive Service Package Used", {"user": frappe.session.user})
    limit_storage = 0
    if doc_package_used:
        service_package_name = doc_package_used.service_package
        doc_service_package = frappe.get_doc("Drive Service Package", {'code': service_package_name})
        limit_storage = doc_service_package.storage_volume * 1073741824
    else:
        name, storage_volume =  frappe.db.get_value("Drive Service Package", {"unit_price": 0}, ["name", "storage_volume"])
        doc_service_package_used = frappe.new_doc('Drive Service Package Used')
        doc_service_package_used.user = frappe.session.user
        doc_service_package_used.service_package = name
        doc_service_package_used.insert(ignore_permissions=True)
        limit_storage = storage_volume * 1073741824
    return {"limit": limit_storage}

@frappe.whitelist()
def get_max_pupv():
    doc_package_used = frappe.db.get("Drive Service Package Used", {"user": frappe.session.user})
    limit_pupv = 0
    if doc_package_used:
        service_package_name = doc_package_used.service_package
        doc_service_package = frappe.get_doc("Drive Service Package", {'code': service_package_name})
        limit_pupv = doc_service_package.pupv
    else:
        name, pupv =  frappe.db.get_value("Drive Service Package", {"unit_price": 0}, ["name", "pupv"])
        doc_service_package_used = frappe.new_doc('Drive Service Package Used')
        doc_service_package_used.user = frappe.session.user
        doc_service_package_used.service_package = name
        doc_service_package_used.insert(ignore_permissions=True)
        limit_pupv = pupv
    return {"limit": limit_pupv}

def validate_quota():
    """
    Fetch user storage quota
    formatted the same as `get_max_storage()`
    """
    quota_limit = frappe.db.get_value(
        "Drive User Storage Quota",
        {"User": frappe.session.user},
        ["user_storage_limit"],
    )
    if quota_limit:
        return int(quota_limit * 1024**2)


@frappe.whitelist()
def get_owned_files_by_storage():
    entities = frappe.db.get_list(
        "Drive Entity",
        filters={"owner": frappe.session.user, "is_group": False},
        order_by="file_size desc",
        fields=["name", "title", "owner", "file_size", "file_kind", "mime_type"],
    )
    DriveEntity = frappe.qb.DocType("Drive Entity")
    query = (
        frappe.qb.from_(DriveEntity)
        .select(DriveEntity.file_kind, fn.Sum(DriveEntity.file_size).as_("file_size"))
        .where((DriveEntity.is_group == 0) & (DriveEntity.owner == frappe.session.user))
        .groupby(DriveEntity.file_kind)
    )
    total = query.run(as_dict=True)
    return {"entities": entities, "total": total}


@frappe.whitelist()
def total_storage_used():
    DriveEntity = frappe.qb.DocType("Drive Entity")
    query = frappe.qb.from_(DriveEntity).select(fn.Sum(DriveEntity.file_size).as_("total_size"))
    result = query.run(as_dict=True)
    return result


@frappe.whitelist()
def total_storage_used_by_user():
    DriveEntity = frappe.qb.DocType("Drive Entity")
    query = (
        frappe.qb.from_(DriveEntity)
        .where(DriveEntity.owner == frappe.session.user)
        .select(fn.Sum(DriveEntity.file_size).as_("total_size"))
    )
    result = query.run(as_dict=True)
    return result


@frappe.whitelist()
def total_storage_used_by_file_kind():
    DriveEntity = frappe.qb.DocType("Drive Entity")
    query = (
        frappe.qb.from_(DriveEntity)
        .select(DriveEntity.file_kind, fn.Sum(DriveEntity.file_size).as_("total_size"))
        .where((DriveEntity.is_group == 0) & (DriveEntity.owner == frappe.session.user))
        .groupby(DriveEntity.file_kind)
    )
    return query.run(as_dict=True)

@frappe.whitelist()
def total_pupv_used_by_user():
    TaskQueue = frappe.qb.DocType("Drive Task Queue")
    query = (
        frappe.qb.from_(TaskQueue)
        .where((TaskQueue.owner == frappe.session.user) & (TaskQueue.status=="Success"))
        .select(fn.Sum(TaskQueue.pupv).as_("total_pupv"))
    )
    result = query.run(as_dict=True)
    return result

def get_storage_allowed():
    limit = get_max_storage()
    total_limit = int(limit.get("limit"))
    total_usage = int(total_storage_used()[0].total_size or 0)
    total_rem = total_limit - total_usage
    if limit.get("quota") is not None:
        quota_limit = int(limit.get("quota"))
        usr_usage = int(total_storage_used_by_user()[0].total_size or 0)
        usr_rem = quota_limit - usr_usage
        return min(usr_rem, total_rem)
    else:
        return total_rem
    


def total_disk_storage_used():
    try:
        from drive.utils.files import get_user_directory

        user_directory = get_user_directory()
        # -sb doesnt work on macos
        cmd = f"du -sb {Path(user_directory.path)} | cut -f1"
        result = os.popen(cmd)
        size = result.read().strip()
    except:
        size = "0M"
    return size


def add_new_site_config_key(key, val):
    site_path = frappe.get_site_path()
    site_config_path = os.path.join(site_path, "site_config.json")

    with open(site_config_path, "r") as f:
        site_config = json.load(f)

    site_config[str(key)] = str(val)

    with open(site_config_path, "w") as f:
        json.dump(site_config, f, indent=2)
