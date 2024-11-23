import frappe

def total_process_unit_use():
    process_unit_use = 0
    process_units = frappe.get_list('Drive Process Unit',
        filters={
            'owner': frappe.session.user
        },
        fields=['process_unit']
    )
    for process in process_units:
        process_unit_use += process["process_unit"]
    return process_unit_use