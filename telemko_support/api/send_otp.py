# apps/telemko_support/telemko_support/api/send_otp.py
import frappe
import random
from frappe.core.doctype.sms_settings.sms_settings import send_sms

@frappe.whitelist(allow_guest=True)
def send_otp(mobile_no):
    if not mobile_no or len(mobile_no) < 10:
        frappe.throw("Valid mobile number is required")

    # Check if customer exists
    customer = frappe.db.exists("Customer", {"mobile_no": mobile_no})
    if not customer:
        frappe.throw("Customer not registered with this mobile number")

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with expiry (10 minutes)
    frappe.cache().set_value(f"otp_{mobile_no}", otp, expires_in_sec=600)
    
    # Send SMS
    message = f"Your Telemko login OTP is {otp}. Valid for 10 minutes. - Telemko"
    try:
        send_sms([mobile_no], message)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "SMS Failed")
        frappe.throw("Failed to send OTP. Please try again.")

    return {"status": "sent", "message": "OTP sent successfully"}