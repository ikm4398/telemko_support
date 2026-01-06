import frappe

@frappe.whitelist(allow_guest=True)
def verify_customer_and_user(mobile_no):
    if not mobile_no:
        return {
            "status": "error",
            "message": "Mobile number is required"
        }

    # ---- Check Customer ----
    customer = frappe.db.get_value(
        "Customer",
        {"mobile_no": mobile_no},
        ["name", "customer_name", "mobile_no", "email_id"],
        as_dict=True
    )

    # ---- Check User ----
    user = frappe.db.get_value(
        "User",
        {"mobile_no": mobile_no},
        ["name", "email", "enabled"],
        as_dict=True
    )

    return {
        "status": "success",
        "mobile_no": mobile_no,
        "customer_exists": bool(customer),
        "user_exists": bool(user),
        "customer": customer,
        "user": user
    }
