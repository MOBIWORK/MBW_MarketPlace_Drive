import frappe


def after_install():
    frappe.db.sql(
        """ALTER TABLE `tabDrive Entity` ADD FULLTEXT INDEX drive_entity_title_fts_idx (title)"""
    )
    add_default_service_packages()
    frappe.db.commit()  

def add_default_service_packages():
    service_packages = [
        {
            'title': "FREE",
            'show': True,
            'storage_volume': 5,
            'pupv': 100,
            'unit_price': 0
        },{
            'title': "STANDARD-1",
            'show': True,
            'storage_volume': 50,
            'pupv': 1000,
            'unit_price': 1000000
        },{
            'title': "STANDARD-2",
            'show': True,
            'storage_volume': 100,
            'pupv': 2000,
            'unit_price': 3000000
        },{
            'title': "STANDARD-3",
            'show': True,
            'storage_volume': 250,
            'pupv': 3000,
            'unit_price': 5000000
        },{
            'title': "STANDARD-4",
            'show': True,
            'storage_volume': 500,
            'pupv': 6000,
            'unit_price': 10000000
        },{
            'title': "STANDARD-5",
            'show': True,
            'storage_volume': 1024,
            'pupv': 12000,
            'unit_price': 20000000
        }
    ]
    for service_package in service_packages:
        if frappe.db.exists("Drive Service Package", {"title": service_package["title"]}):
            continue

        doc = frappe.new_doc("Drive Service Package")
        doc.title = service_package["title"]
        doc.show = service_package["show"]
        doc.storage_volume = service_package["storage_volume"]
        doc.pupv = service_package["pupv"]
        doc.unit_price = service_package["unit_price"]
        doc.insert(ignore_permissions=True)
