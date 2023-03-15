# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from frappe.utils.password import update_password

class FirebaseIntegration(Document):
	pass

default_app = None


def initialize_app():
	global default_app
	if default_app: return
	firebase_server_key = frappe.db.get_single_value("Firebase Integration", "firebase_server_key")
	# try:
	cred = credentials.Certificate(firebase_server_key)
	default_app = firebase_admin.initialize_app(cred)
	# except:
	# 	frappe.throw("Unable to initialize firebase app")

@frappe.whitelist(allow_guest=True)
def verify_user_token():
	initialize_app()
	id_token = frappe.form_dict.id_token
	decoded_token = auth.verify_id_token(id_token)
	uid = decoded_token['uid']
	return {"msg": uid}

@frappe.whitelist(allow_guest=True)
def complete_user_mobile_signup():
	id_token = frappe.form_dict.id_token
	password = frappe.form_dict.password
	full_name = frappe.form_dict.full_name

	decoded_token = auth.verify_id_token(id_token)
	mobile_phone= decoded_token['phone_number']
	if frappe.db.exists("User", {"mobile_no": mobile_phone}): return {"error": _("This mobile number is used before")}
	user_doc = frappe.get_doc({
		"doctype": "User",
		"mobile_no": mobile_phone,
		"first_name": full_name,
	})
	user_doc.insert(ignore_permissions=True)

	update_password(user_doc.name, password)
	frappe.db.commit()

	return {"msg": _("The user has been registered successfully")}