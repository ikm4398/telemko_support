# telemko_support/api/registration/utils.py
import frappe

def parse_name(full_name):
    """Split name into first & last name"""
    parts = full_name.strip().split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first_name, last_name


def get_or_create_customer(mobile_no, customer_name, email_id):
    customer = frappe.db.get_value("Customer", {"mobile_no": mobile_no}, "name")

    if customer:
        frappe.db.set_value("Customer", customer, "email_id", email_id)
        return customer

    cust = frappe.new_doc("Customer")
    # cust.flags.ignore_permissions = True  # Handled in caller
    cust.flags.ignore_mandatory = True

    cust.customer_name = customer_name
    cust.customer_type = "Individual"
    cust.customer_group = "Individual"  # ← change if you use different group
    cust.territory = "All Territories"
    cust.mobile_no = mobile_no
    cust.email_id = email_id

    cust.insert()
    frappe.db.commit()
    return cust.name


def get_or_create_contact(mobile_no, first_name, last_name, email_id, customer):
    """
    Fixed: customer is now docname (not customer_name/title)
    """
    contact = frappe.db.get_value("Contact", {"mobile_no": mobile_no}, "name")

    if contact:
        frappe.db.set_value("Contact", contact, "email_id", email_id)
        return contact

    contact_doc = frappe.new_doc("Contact")
    # contact_doc.flags.ignore_permissions = True  # Handled in caller
    contact_doc.flags.ignore_link_validation = True  # Extra safety for links

    contact_doc.first_name = first_name
    contact_doc.last_name = last_name
    contact_doc.mobile_no = mobile_no
    contact_doc.phone = mobile_no
    contact_doc.email_id = email_id

    contact_doc.append("links", {
        "link_doctype": "Customer",
        "link_name": customer  # ← Use docname, not title
    })

    contact_doc.insert()
    frappe.db.commit()
    return contact_doc.name