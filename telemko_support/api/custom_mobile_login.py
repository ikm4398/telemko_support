# apps/telemko_support/telemko_support/api/custom_mobile_login.py
import frappe
from frappe.auth import LoginManager
from frappe.sessions import clear_sessions

@frappe.whitelist(allow_guest=True)
def mobile_login(mobile_no, otp):
    if not mobile_no or not otp:
        frappe.throw("Mobile number and OTP are required")

    # Verify OTP first
    verify_result = frappe.call("telemko_support.api.verify_otp.verify_otp", mobile_no=mobile_no, otp=otp)
    
    if not verify_result or verify_result.get("status") != "verified":
        frappe.throw("Invalid or expired OTP")

    user = verify_result.get("user")
    if not user:
        frappe.throw("User not found")

    # --- Proper OTP-based login without password ---
    # Create login manager instance
    login_manager = LoginManager()

    # Directly set the authenticated user (bypasses password check safely)
    frappe.set_user(user)

    # Initialize the session properly
    login_manager.user = user
    login_manager.post_login()

    # Optional: Clear previous sessions of this user (recommended for mobile)
    clear_sessions(user=user, keep_current=True)

    # Return success with session details
    full_name = frappe.get_cached_doc("User", user).get("full_name") or user

    return {
        "message": "Login successful",
        "sid": frappe.session.sid,
        "user": user,
        "full_name": full_name,
        "roles": frappe.get_roles(user)
    }