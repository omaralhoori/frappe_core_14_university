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
	id_token = frappe.form_dict.id_token
	res = verify_token(id_token)
	if frappe.db.exists("User", {"mobile_no": res.get("user")}): 
		# return {"error": _("This mobile number is used before")}
		login_user(res.get("user"))
		return {"msg": _("The user has been registered successfully"), "redirect_to": "/me"}
	return res

def verify_token(token: str) -> dict[str, str]:
	initialize_app()
	decoded_token = auth.verify_id_token(token)
	uid = decoded_token['uid']
	return {"msg": uid, "user": format_mobile_number(decoded_token['phone_number'])}

@frappe.whitelist(allow_guest=True)
def complete_user_mobile_signup():
	id_token = frappe.form_dict.id_token
	password = frappe.form_dict.password
	full_name = frappe.form_dict.full_name
	student_nationality = frappe.form_dict.student_nationality
	student_language = frappe.form_dict.student_language
	student_dob = frappe.form_dict.student_dob
	educational_certificate = frappe.form_dict.educational_certificate
	educational_level = frappe.form_dict.educational_level
	student_country = frappe.form_dict.student_country
	student_city = frappe.form_dict.student_city
	student_status = frappe.form_dict.student_status
	student_gender = frappe.form_dict.student_gender
	initialize_app()
	decoded_token = auth.verify_id_token(id_token)
	mobile_phone= format_mobile_number(decoded_token['phone_number'])
	if frappe.db.exists("User", {"mobile_no": mobile_phone}): return {"error": _("This mobile number is used before")}
	user_doc = frappe.get_doc({
		"doctype": "User",
		"mobile_no": mobile_phone,
		"first_name": full_name,
	})
	user_doc.insert(ignore_permissions=True)
	from education.education.doctype.student_applicant.student_applicant import create_student_by_user
	create_student_by_user(user_doc, {
		"student_nationality": student_nationality,
		"student_language": student_language,
		"student_dob":student_dob,
		"educational_certificate":educational_certificate,
		"educational_level":educational_level,
		"student_country":student_country,
		"student_city":student_city,
		"student_status":student_status,
		"student_gender":student_gender,
	} )
	update_password(user_doc.name, password)
	frappe.db.commit()
	login_user(mobile_phone)
	return {"msg": _("The user has been registered successfully"), "redirect_to": "/me"}

@frappe.whitelist(allow_guest=True)
def test_user_mobile_signup():
	password = frappe.form_dict.password
	full_name = frappe.form_dict.full_name
	user_id = frappe.form_dict.user_id
	mobile_phone= format_mobile_number(user_id)
	if frappe.db.exists("User", {"mobile_no": mobile_phone}): return {"error": _("This mobile number is used before")}
	user_doc = frappe.get_doc({
		"doctype": "User",
		"mobile_no": mobile_phone,
		"first_name": full_name,
	})
	user_doc.insert(ignore_permissions=True)
	from education.education.doctype.student_applicant.student_applicant import create_student_by_user
	create_student_by_user(user_doc)
	update_password(user_doc.name, password)
	frappe.db.commit()
	return {"msg": _("The user has been registered successfully"), "redirect_to": "/me"}

def login_user(user):
	login_manager = frappe.auth.LoginManager()
	login_manager.authenticate(user=user, pwd=user, validate_password=False)
	login_manager.post_login()

def format_mobile_number(mobile_number):
	if mobile_number and mobile_number.startswith("+"):
		return mobile_number[1:]
	return mobile_number