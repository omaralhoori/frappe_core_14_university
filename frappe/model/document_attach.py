import frappe
import os

from frappe.utils.file_manager import save_file

class DocumentAttach:
	def attach(self, file, file_name, is_private=True):
		save_file(fname=file_name, content =file, dt= self.doctype, dn=self.name, is_private=is_private)
		# if is_private:
		# 	site_path = frappe.local.site + "/public/files/"
		# 	file_url = "/files/"
		# else:
		# 	site_path = frappe.local.site + "/private/files/"
		# 	file_url = "/private/files/"
		# created = save_file(site_path, self.name + '-' + file_name, file)
		# if created:
		# 	add_attachment(self.doctype, self.name, file_url + self.name + "-" + file_name, is_private)

# def save_file(file_path, file_name, file):
    

#     with open(os.path.join( file_path, file_name), "wb") as f:
#         f.write(file)

# def add_attachment(dt, dn, file_url, is_private):
# 	file_doc = frappe.get_doc({
# 		"doctype": "File",
# 		"file_name": file_url.split("/")[-1],
# 		"file_url": file_url,
# 		"is_private": is_private,
# 		"attached_to_name": dn,
# 		"attached_to_doctype": dt
# 	})
# 	file_doc.save(ignore_permissions=True)