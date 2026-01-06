# apps/telemko_support/telemko_support/api/verify_otp.py
import frappe

@frappe.whitelist(allow_guest=True)
def verify_otp(mobile_no, otp):
    if not mobile_no or not otp:
        frappe.throw("Mobile number and OTP are required")

    cached_otp = frappe.cache().get_value(f"otp_{mobile_no}")
    
    if not cached_otp:
        frappe.throw("OTP expired or not found")

    if str(cached_otp) != str(otp).strip():
        frappe.throw("Invalid OTP")

    # Clear OTP after successful verification
    frappe.cache().delete_value(f"otp_{mobile_no}")

    # Find Customer by mobile_no
    customer_name = frappe.db.exists("Customer", {"mobile_no": mobile_no})
    if not customer_name:
        frappe.throw("Customer not registered with this mobile number")

    customer = frappe.get_doc("Customer", customer_name)

    # Find linked Frappe User - PRIORITY ORDER:
    # 1. User with this mobile as username (most common in your case)
    # 2. User with this mobile in phone field
    # 3. User with same email as customer
    user = None

    # Option 1: Mobile number is the username (your current setup)
    user = frappe.db.get_value("User", {"name": mobile_no, "enabled": 1}, "name")

    # Option 2: Mobile in phone field
    if not user:
        user = frappe.db.get_value("User", {"phone": mobile_no, "enabled": 1}, "name")

    # Option 3: Same email as customer
    if not user and customer.email_id:
        user = frappe.db.get_value("User", {"email": customer.email_id, "enabled": 1}, "name")

    if not user:
        frappe.throw("No active Frappe user account linked to this mobile number. Please contact admin.")

    return {
        "status": "verified",
        "user": user,
        "customer": customer.name
    }