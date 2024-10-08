# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

	context.current_user = frappe.get_doc("User", frappe.session.user)
	context.show_sidebar = True
	context.messages = get_messages()
	context.events = get_events()
	print(context.events)

def get_events():
	return frappe.db.sql("""
		SELECT subject FROM `tabEvent` 
		WHERE status='Open' AND event_type='Public' AND event_category='Event'
		AND starts_on <= NOW() AND ends_on >= NOW()
		ORDER BY creation desc
	""", as_dict=True)
def get_messages():
	user = frappe.session.user
	student = frappe.db.get_value("Student", {"user": user}, ['name'])
	if not student: return []

	groups = frappe.db.sql("""
		SELECT grpStd.parent as name FROM `tabStudent Group Student` as grpStd
		WHERE student=%(student)s AND active=1
	""", {"student": student}, as_dict=True)

	messages = frappe.db.sql("""
		SELECT name, message, 'Student Message' as message_type FROM `tabStudent Message`
		WHERE student=%(student)s AND is_seen='0'
		ORDER BY send_date
	""", {"student": student}, as_dict=True)
	if len(groups) > 0:
		student_groups = []
		for group in groups:
			student_groups.append('"' + group.get('name') + '"')
			groups = ",".join(student_groups)
		group_messages = frappe.db.sql("""
			SELECT name, message, 'Group Message' as message_type FROM `tabGroup Message`
			WHERE student_group IN ({groups}) AND (seen_by IS NULL or seen_by NOT LIKE "%'{user}'%")
		""".format(groups=groups, user=user), as_dict=True)
		messages.extend(group_messages)	
	return messages


@frappe.whitelist()
def dismiss_message(doctype, docname):
	if doctype=='Student Message':
		frappe.db.sql("""
			UPDATE `tabStudent Message` SET is_seen=1
			WHERE name=%(docname)s
		""", {"docname": docname})
	elif doctype == 'Group Message':	
		frappe.db.sql("""
			UPDATE `tabGroup Message` SET seen_by=concat(ifnull(seen_by,""), "'{user}'")
			WHERE name=%(docname)s
		""".format(user=frappe.session.user), {"docname": docname})
	frappe.db.commit()