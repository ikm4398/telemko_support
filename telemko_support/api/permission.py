import frappe

def has_app_permission(user=None):
    # allow access to all logged-in users
    return True
