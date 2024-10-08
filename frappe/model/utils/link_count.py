# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe

ignore_doctypes = ("DocType", "Print Format", "Role", "Module Def", "Communication", "ToDo")


def notify_link_count(doctype, name):
	"""updates link count for given document"""
	if hasattr(frappe.local, "link_count"):
				
		if type(name) == list: name = name[0]
		if (doctype, name) in frappe.local.link_count:
			frappe.local.link_count[(doctype, name)] += 1
		else:
			frappe.local.link_count[(doctype, name)] = 1


def flush_local_link_count():
	"""flush from local before ending request"""
	if not getattr(frappe.local, "link_count", None):
		return

	link_count = frappe.cache().get_value("_link_count")
	if not link_count:
		link_count = {}

		for key, value in frappe.local.link_count.items():
			if key in link_count:
				link_count[key] += frappe.local.link_count[key]
			else:
				link_count[key] = frappe.local.link_count[key]

	frappe.cache().set_value("_link_count", link_count)


def update_link_count():
	"""increment link count in the `idx` column for the given document"""
	link_count = frappe.cache().get_value("_link_count")

	if link_count:
		for key, count in link_count.items():
			if key[0] not in ignore_doctypes:
				try:
					frappe.db.sql(
						f"update `tab{key[0]}` set idx = idx + {count} where name=%s",
						key[1],
						auto_commit=1,
					)
				except Exception as e:
					if not frappe.db.is_table_missing(e):  # table not found, single
						raise e
	# reset the count
	frappe.cache().delete_value("_link_count")
