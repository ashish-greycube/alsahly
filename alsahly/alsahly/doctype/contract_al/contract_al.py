# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, cstr

class ContractAL(Document):
	def validate(self):
		self.validate_contract_dates()
	
	def validate_contract_dates(self):
		if getdate(self.contract_start_date) > getdate(self.contract_end_date):
			frappe.throw(_("Contract Start Date Cann't be Greatee than Contract End Date."))

	@frappe.whitelist()
	def get_items(self):
		item_list = frappe.db.get_all('Item', filters={"item_group": self.sub_item_group},fields=['name','standard_rate', 'stock_uom'])
		print("item_list=========>", item_list)
		return item_list

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_item_group(doctype, txt, searchfield, start, page_len, filters):
		
		item_group_list = frappe.get_all("Item Group", filters={"is_group":0}, fields=["distinct parent_item_group"], as_list=1)
		unique = tuple(set(item_group_list))
		# print(unique, '----------ab')
		return unique

