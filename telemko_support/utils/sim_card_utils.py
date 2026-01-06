import frappe
from frappe import _

@frappe.whitelist()
def get_device_stock_items(doctype, txt, searchfield, start, page_len, filters):
    """
    Custom query to fetch Device Stock Item rows for a given parent (Device Stock 2).
    """
    if not filters.get("parent") or not filters.get("parenttype"):
        frappe.msgprint(_("Please select a Device first"))
        return []

    if doctype != "Device Stock Item":
        frappe.throw(_("Invalid doctype specified"))

    fltr = {
        "parent": filters.get("parent"),
        "parenttype": filters.get("parenttype")
    }
    if txt:
        fltr[searchfield] = ("like", f"%{txt}%")

    try:
        results = frappe.get_all(
            "Device Stock Item",
            filters=fltr,
            fields=["name", "device_name"],
            start=start,
            page_length=page_len,
            order_by="name",
            ignore_permissions=True
        )
        return [[row.name, row.device_name or row.name] for row in results]
    except Exception as e:
        frappe.log_error(f"Error in get_device_stock_items: {str(e)}", "Device Stock Item Query")
        return []

@frappe.whitelist()
def get_device_stock_item_data(device_item, parent, parenttype):
    """
    Fetch specific fields from a Device Stock Item record, bypassing permissions.
    """
    if not device_item or not parent or not parenttype:
        frappe.throw(_("Device Item and Parent are required"))

    if parenttype != "Device Stock 2":
        frappe.throw(_("Invalid parent type specified"))

    try:
        data = frappe.get_all(
            "Device Stock Item",
            filters={
                "name": device_item,
                "parent": parent,
                "parenttype": parenttype
            },
            fields=["device_name", "imei", "status", "sim_number", "sim_carrier"],
            ignore_permissions=True
        )
        if not data:
            frappe.throw(_("Device Stock Item not found or access denied"))
        return data[0]
    except Exception as e:
        frappe.log_error(f"Error in get_device_stock_item_data: {str(e)}", "Device Stock Item Data Fetch")
        frappe.throw(_("Failed to fetch Device Stock Item data: {}".format(str(e))))