import frappe
import random
from frappe.core.doctype.sms_settings.sms_settings import send_sms

@frappe.whitelist(allow_guest=False)
def send_registration_otp(mobile_no):
    """
    Send OTP only for NEW registration.
    Blocks if user already exists with this mobile number.
    """
    if not mobile_no or len(mobile_no) != 10 or not mobile_no.isdigit():
        frappe.throw("Valid 10-digit mobile number is required")

    # Check existing active user
    existing_user = frappe.db.get_value(
        "User",
        {"mobile_no": mobile_no, "enabled": 1},
        "name"
    )

    if existing_user:
        frappe.throw("User already exists. Please login instead.")

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Cache for 10 minutes
    frappe.cache().set_value(
        f"registration_otp_{mobile_no}",
        otp,
        expires_in_sec=600
    )

    # Prepare message
    message = f"Your Telemko registration OTP is {otp}. Valid for 10 minutes."

    try:
        send_sms([mobile_no], message)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Registration OTP SMS Failed")
        frappe.throw("Failed to send OTP. Please try again later.")

    return {
        "status": "sent",
        "message": "Registration OTP sent successfully"
    }


# # telemko_support/api/registration/send_otp.py
# import frappe
# import random
# # from frappe.core.doctype.sms_settings.sms_settings import send_sms  # disabled for debug

# @frappe.whitelist(allow_guest=True)
# def send_registration_otp(mobile_no):
#     """
#     Send OTP only for NEW registration.
#     DEBUG MODE:
#     - Prints OTP
#     - Does NOT send SMS
#     """
#     if not mobile_no or len(mobile_no) != 10 or not mobile_no.isdigit():
#         frappe.throw("Valid 10-digit mobile number is required")

#     # Check existing active user
#     existing_user = frappe.db.get_value(
#         "User",
#         {"mobile_no": mobile_no, "enabled": 1},
#         "name"
#     )

#     if existing_user:
#         frappe.throw("User already exists. Please login instead.")

#     # Generate 6-digit OTP
#     otp = str(random.randint(100000, 999999))

#     # Cache for 10 minutes
#     frappe.cache().set_value(
#         f"registration_otp_{mobile_no}",
#         otp,
#         expires_in_sec=600
#     )

#     # DEBUG: print OTP in bench console / logs
#     print(f"[DEBUG] Registration OTP for {mobile_no}: {otp}")
#     frappe.logger().info(f"[DEBUG] Registration OTP for {mobile_no}: {otp}")

#     # SMS sending disabled (quota-safe)
#     # message = f"Your Telemko registration OTP is {otp}. Valid for 10 minutes."
#     # send_sms([mobile_no], message)

#     return {
#         "status": "sent",
#         "message": "Registration OTP generated (SMS disabled in debug mode)",
#         "otp": otp  # optional: remove this in production
#     }
