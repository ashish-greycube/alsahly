import frappe
from frappe import _
from frappe.utils import cstr

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_contract_items_list(doctype, txt, searchfield, start, page_len, filters):
	contract_no = filters.get("contract_no")
	print("==================contract_no=============", contract_no)
	return frappe.get_all(
		"Contract Items Details AL",
		parent_doctype="Contract AL",
		filters={"parent": contract_no},
		fields=["distinct item_code, item_name"],
		as_list=1,
	)

@frappe.whitelist()
def get_item_rate_from_contarct_type(custom_contract_no, item_code):
	item_rate = frappe.db.get_value("Contract Items Details AL", {"parent": custom_contract_no, "item_code": item_code}, 'rate')
	return item_rate or 0

def set_internal_wo_reference_in_so(self, method):
		if self.custom_work_order_no and self.custom_work_order_type:
			self.custom_internal_wo_reference = cstr(self.custom_work_order_no) + cstr(self.custom_work_order_type)