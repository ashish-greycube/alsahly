import frappe
from frappe import _
from frappe.utils import cstr, cint

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
		if self.custom_work_order_no:
			print(len(self.custom_work_order_no), "==========length")
			work_order_no = cint(self.custom_work_order_no)
			if work_order_no == 0:
				frappe.throw(_("Only Digits are allowed in Work Order No."))
			if len(self.custom_work_order_no) <= 15:
				frappe.throw(_("Work Order No Digits need to be more than 15 Digits"))
			print(work_order_no, "========work_order_no")

		# if self.custom_work_order_no and self.custom_work_order_type:
		self.custom_internal_wo_reference = (self.custom_work_order_no or '') + cstr(self.custom_work_order_type or '')

def set_cc_and_project_from_so(self, method):
	if len(self.items)>0:
		for item in self.items:
			if item.sales_order:
				cost_center, project = frappe.db.get_value("Sales Order",item.sales_order,["cost_center","project"])
				item.cost_center = cost_center
				item.project = project