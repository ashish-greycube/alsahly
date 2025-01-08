# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, cstr, cint

class ContractAL(Document):
	def validate(self):
		self.validate_contract_dates()
		self.validate_government_contract_no()
	
	def validate_contract_dates(self):
		if getdate(self.contract_start_date) > getdate(self.contract_end_date):
			frappe.throw(_("Contract Start Date Can't be Greater than Contract End Date."))

	def validate_government_contract_no(self):
		print(len(self.government_contract_no))
		int_contract_no = cint(self.government_contract_no)
		if int_contract_no == 0:
			frappe.throw(_("Government Contract No. must have digit only"))
		
	@frappe.whitelist()
	def get_items(self):
		item_list = frappe.db.get_all('Item', filters={"item_group": self.sub_item_group},fields=['name','standard_rate', 'stock_uom'])
		print("item_list=========>", item_list)
		if len(item_list)>0:
			for item in item_list:
				item_selling_price = frappe.db.get_all("Item Price",
										   filters={"selling":1,"item_code":item.name},
										   fields=["price_list_rate"],limit=1)
				if len(item_selling_price)>0:
					item["price_list_rate"]=item_selling_price[0].price_list_rate
		return item_list

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_item_group(doctype, txt, searchfield, start, page_len, filters):
		
		item_group_list = frappe.get_all("Item Group", 
								   filters={"is_group":0,"parent_item_group": ("like", f"{txt}%")}, 
								   fields=["parent_item_group"], as_list=1)
		unique = tuple(set(item_group_list))
		return unique

