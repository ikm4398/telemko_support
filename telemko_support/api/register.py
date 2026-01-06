# import frappe
# import random
# from frappe.core.doctype.sms_settings.sms_settings import send_sms


# # ---------------------------------------------------------
# # SEND REGISTRATION OTP
# # ---------------------------------------------------------
# @frappe.whitelist(allow_guest=True)
# def send_registration_otp(mobile_no):
#     """
#     Send OTP only for NEW registration.
#     Block if a User already exists with this mobile.
#     """

#     if not mobile_no or len(mobile_no) < 10:
#         frappe.throw("Valid 10-digit mobile number is required")

#     # Check existing user by mobile
#     existing_user = frappe.db.get_value(
#         "User",
#         {"mobile_no": mobile_no, "enabled": 1},
#         "name"
#     )

#     if existing_user:
#         frappe.throw("User already exists. Please login instead.")

#     # Generate OTP
#     otp = str(random.randint(100000, 999999))

#     # Cache OTP for 10 minutes
#     frappe.cache().set_value(
#         f"registration_otp_{mobile_no}",
#         otp,
#         expires_in_sec=600
#     )

#     # Send SMS
#     message = f"Your Telemko registration OTP is {otp}. Valid for 10 minutes."
#     try:
#         send_sms([mobile_no], message)
#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Registration OTP SMS Failed")
#         frappe.throw("Failed to send OTP. Please try again later.")

#     return {
#         "status": "sent",
#         "message": "Registration OTP sent successfully"
#     }


# # ---------------------------------------------------------
# # COMPLETE REGISTRATION
# # ---------------------------------------------------------
# @frappe.whitelist(allow_guest=True)
# def complete_registration(mobile_no, otp, customer_name, email_id):
#     """
#     Verify OTP and complete registration:
#     - Create Customer
#     - Create Contact
#     - Create User (email-based)
#     """

#     if not mobile_no or not otp or not customer_name or not email_id:
#         frappe.throw("Mobile number, OTP, name, and email are required")

#     # -------------------------------------------------
#     # VERIFY OTP
#     # -------------------------------------------------
#     cached_otp = frappe.cache().get_value(f"registration_otp_{mobile_no}")

#     if not cached_otp:
#         frappe.throw("OTP expired or not found")

#     if str(cached_otp) != str(otp).strip():
#         frappe.throw("Invalid OTP")

#     frappe.cache().delete_value(f"registration_otp_{mobile_no}")

#     # -------------------------------------------------
#     # PARSE NAME
#     # -------------------------------------------------
#     parts = customer_name.strip().split()
#     first_name = parts[0]
#     last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

#     # -------------------------------------------------
#     # CUSTOMER (NO DEFAULT LOOKUPS)
#     # -------------------------------------------------
#     customer = frappe.db.get_value(
#         "Customer", {"mobile_no": mobile_no}, "name"
#     )

#     if not customer:
#         cust = frappe.new_doc("Customer")
#         cust.flags.ignore_permissions = True
#         cust.flags.ignore_validate = True
#         cust.flags.ignore_defaults = True
#         cust.flags.ignore_mandatory = True

#         cust.customer_name = customer_name
#         cust.customer_type = "Individual"
#         cust.customer_group = "Individual"
#         cust.territory = "All Territories"
#         cust.mobile_no = mobile_no
#         cust.email_id = email_id

#         cust.insert()
#         frappe.db.commit()
#         customer = cust.name
#     else:
#         frappe.db.set_value("Customer", customer, "email_id", email_id)

#     # -------------------------------------------------
#     # CONTACT
#     # -------------------------------------------------
#     contact = frappe.db.get_value(
#         "Contact", {"mobile_no": mobile_no}, "name"
#     )

#     if not contact:
#         contact_doc = frappe.new_doc("Contact")
#         contact_doc.flags.ignore_permissions = True

#         contact_doc.first_name = first_name
#         contact_doc.last_name = last_name
#         contact_doc.mobile_no = mobile_no
#         contact_doc.phone = mobile_no
#         contact_doc.email_id = email_id

#         contact_doc.append("links", {
#             "link_doctype": "Customer",
#             "link_name": customer
#         })

#         contact_doc.insert()
#         frappe.db.commit()
#         contact = contact_doc.name
#     else:
#         frappe.db.set_value("Contact", contact, "email_id", email_id)

#     # -------------------------------------------------
#     # USER (EMAIL MUST BE REAL)
#     # -------------------------------------------------
#     if frappe.db.exists("User", email_id):
#         frappe.throw("An account already exists with this email")

#     user = frappe.new_doc("User")
#     user.flags.ignore_permissions = True

#     user.email = email_id              # ✅ VALID EMAIL
#     user.first_name = first_name
#     user.last_name = last_name
#     user.username = mobile_no          # ✅ MOBILE AS USERNAME
#     user.mobile_no = mobile_no
#     user.phone = mobile_no
#     user.enabled = 1
#     user.user_type = "Website User"
#     user.send_welcome_email = 0

#     user.insert()
#     frappe.db.commit()

#     user.add_roles("Customer")

#     # Link User → Contact
#     frappe.db.set_value("Contact", contact, "user", user.name)

#     return {
#         "status": "success",
#         "message": "Registration completed successfully. You can now login with OTP.",
#         "user": user.name,
#         "customer": customer,
#         "contact": contact
#     }
import frappe
import random
from frappe.core.doctype.sms_settings.sms_settings import send_sms


# ---------------------------------------------------------
# SEND REGISTRATION OTP
# ---------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def send_registration_otp(mobile_no):
    """
    Send OTP only for NEW registration.
    Block if a User already exists with this mobile.
    """

    if not mobile_no or len(mobile_no) != 10 or not mobile_no.isdigit():
        frappe.throw("Valid 10-digit mobile number is required")

    # Check existing user by mobile
    existing_user = frappe.db.get_value(
        "User",
        {"mobile_no": mobile_no, "enabled": 1},
        "name"
    )

    if existing_user:
        frappe.throw("User already exists. Please login instead.")

    # Generate OTP
    otp = str(random.randint(100000, 999999))

    # Cache OTP for 10 minutes
    frappe.cache().set_value(
        f"registration_otp_{mobile_no}",
        otp,
        expires_in_sec=600
    )

    # Send SMS
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


# ---------------------------------------------------------
# COMPLETE REGISTRATION
# ---------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def complete_registration(mobile_no, otp, customer_name, email_id):
    """
    Verify OTP and complete registration:
    - Create Customer
    - Create Contact
    - Create User
    - Link User to Customer (Portal Users)
    """

    if not all([mobile_no, otp, customer_name, email_id]):
        frappe.throw("Mobile number, OTP, name, and email are required")

    # -------------------------------------------------
    # VERIFY OTP
    # -------------------------------------------------
    cached_otp = frappe.cache().get_value(f"registration_otp_{mobile_no}")

    if not cached_otp:
        frappe.throw("OTP expired or not found")

    if str(cached_otp) != str(otp).strip():
        frappe.throw("Invalid OTP")

    frappe.cache().delete_value(f"registration_otp_{mobile_no}")

    # -------------------------------------------------
    # PARSE NAME
    # -------------------------------------------------
    parts = customer_name.strip().split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    # -------------------------------------------------
    # CUSTOMER
    # -------------------------------------------------
    customer = frappe.db.get_value("Customer", {"mobile_no": mobile_no}, "name")

    if not customer:
        cust = frappe.new_doc("Customer")
        cust.flags.ignore_permissions = True
        cust.flags.ignore_validate = True
        cust.flags.ignore_defaults = True
        cust.flags.ignore_mandatory = True

        cust.customer_name = customer_name
        cust.customer_type = "Individual"
        cust.customer_group = "Individual"
        cust.territory = "All Territories"
        cust.mobile_no = mobile_no
        cust.email_id = email_id

        cust.insert()
        frappe.db.commit()
        customer = cust.name
    else:
        frappe.db.set_value("Customer", customer, "email_id", email_id)

    # -------------------------------------------------
    # CONTACT
    # -------------------------------------------------
    contact = frappe.db.get_value("Contact", {"mobile_no": mobile_no}, "name")

    if not contact:
        contact_doc = frappe.new_doc("Contact")
        contact_doc.flags.ignore_permissions = True

        contact_doc.first_name = first_name
        contact_doc.last_name = last_name
        contact_doc.mobile_no = mobile_no
        contact_doc.phone = mobile_no
        contact_doc.email_id = email_id

        contact_doc.append("links", {
            "link_doctype": "Customer",
            "link_name": customer
        })

        contact_doc.insert()
        frappe.db.commit()
        contact = contact_doc.name
    else:
        frappe.db.set_value("Contact", contact, "email_id", email_id)

    # -------------------------------------------------
    # USER
    # -------------------------------------------------
    if frappe.db.exists("User", email_id):
        frappe.throw("An account already exists with this email")

    user = frappe.new_doc("User")
    user.flags.ignore_permissions = True

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

    # Add standard Customer role + custom Mobile User role (if exists)
    user.add_roles("Customer")
    if frappe.db.exists("Role", "Customer Mobile User"):
        user.add_roles("Customer Mobile User")

    # -------------------------------------------------
    # LINK USER → CONTACT
    # -------------------------------------------------
    frappe.db.set_value("Contact", contact, "user", user.name)

    # -------------------------------------------------
    # LINK USER → CUSTOMER (PORTAL USERS)
    # -------------------------------------------------
    if not frappe.db.exists(
        "Customer Portal User",
        {"parent": customer, "user": user.name}
    ):
        cust_doc = frappe.get_doc("Customer", customer)
        cust_doc.flags.ignore_permissions = True

        cust_doc.append("portal_users", {
            "user": user.name
        })

        cust_doc.save()
        frappe.db.commit()

    return {
        "status": "success",
        "message": "Registration completed successfully. You can now login with OTP.",
        "user": user.name,
        "customer": customer,
        "contact": contact
    }
