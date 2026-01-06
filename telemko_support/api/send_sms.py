import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms

@frappe.whitelist(allow_guest=False)
def send_sms_api(receiver_list, message):
    if isinstance(receiver_list, str):
        receiver_list = [r.strip() for r in receiver_list.split(",") if r.strip()]
   
    if not receiver_list or not message:
        frappe.throw("Receiver list and message are required")
   
    send_sms(receiver_list, message)
   
    return {"status": "sent", "receivers": receiver_list, "message": message}