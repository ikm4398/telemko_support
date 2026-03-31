# telemko_support/api/registration/complete_registration.py (renamed from reg.txt for clarity)
import frappe
from frappe.auth import LoginManager
from frappe.sessions import clear_sessions
from .utils import parse_name, get_or_create_customer, get_or_create_contact

@frappe.whitelist(allow_guest=True)
def complete_registration(mobile_no, otp, customer_name, email_id):
    """
    Verify OTP → Create/Update Customer → Contact → User → Portal linking
    → Auto-login and return sid
    """
    if not all([mobile_no, otp, customer_name, email_id]):
        frappe.throw("Mobile number, OTP, name and email are required")

    # ── Verify OTP ─────────────────────────────────────────────
    cached_otp = frappe.cache().get_value(f"registration_otp_{mobile_no}")

    if not cached_otp:
        frappe.throw("OTP expired or not found")

    if str(cached_otp) != str(otp).strip():
        frappe.throw("Invalid OTP")

    frappe.cache().delete_value(f"registration_otp_{mobile_no}")

    # ── Prepare name parts ─────────────────────────────────────
    first_name, last_name = parse_name(customer_name)
    try:
        frappe.set_user("Administrator")
        # ── Customer ───────────────────────────────────────────────
        customer = get_or_create_customer(mobile_no, customer_name, email_id)

        # ── Contact ────────────────────────────────────────────────
        contact = get_or_create_contact(mobile_no, first_name, last_name, email_id, customer)

        # ── User ───────────────────────────────────────────────────
        if frappe.db.exists("User", email_id):
            frappe.throw("An account already exists with this email")

        user = frappe.new_doc("User")
        user.email = email_id
        user.first_name = first_name
        user.last_name = last_name
        user.username = mobile_no          
        user.mobile_no = mobile_no
        user.phone = mobile_no
        user.enabled = 1
        user.user_type = "Website User"
        user.send_welcome_email = 0

        user.insert()
        frappe.db.commit()

        # Add roles
        user.add_roles("Customer")

        # Optional custom role
        if frappe.db.exists("Role", "Customer Mobile User"):
            user.add_roles("Customer Mobile User")

        # ── Link Contact → User ────────────────────────────────────
        frappe.db.set_value("Contact", contact, "user", user.name)

        # ── Link Customer Portal User ──────────────────────────────
        # Fix: use user.name instead of user (which is a string)
        if not frappe.db.exists(
            "Customer Portal User",
            {"parent": customer, "user": user.name}
        ):
            cust_doc = frappe.get_doc("Customer", customer)
            # cust_doc.flags.ignore_permissions = True  # Not needed
            cust_doc.append("portal_users", {"user": user.name})
            cust_doc.save()
            frappe.db.commit()

        # ── AUTO LOGIN ─────────────────────────────────────────────
        try:
            # Proper Frappe login flow (creates session)
            login_manager = LoginManager()
            frappe.set_user(user.name)              
            login_manager.user = user.name
            login_manager.post_login()

            # Recommended for mobile/security: clear old sessions
            clear_sessions(user=user.name, keep_current=True)

            full_name = user.get("full_name") or user.name

            return {
                "status": "success",
                "message": "Registration & auto-login completed successfully",
                "user": user.name,
                "full_name": full_name,
                "customer": customer,
                "contact": contact,
                "sid": frappe.session.sid,           
                "roles": frappe.get_roles(user.name)
            }

        except Exception as e:
            frappe.log_error("Auto-login failed after registration", str(e))
            # Still return success but without sid → client can login normally
            return {
                "status": "partial_success",
                "message": "Registration successful but auto-login failed. Please login normally.",
                "user": user.name,
                "customer": customer,
                "contact": contact
            }

    finally:
        frappe.db.commit()  # Ensure commit after restore