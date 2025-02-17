import frappe
from frappe import _
from frappe.utils import cstr, cint, getdate

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_contract_items_list(doctype, txt, searchfield, start, page_len, filters):
	contract_no = filters.get("contract_no")
	print("==================contract_no=============", contract_no)
	return frappe.get_all(
		"Contract Items Details AL",
		parent_doctype="Contract AL",
		filters={"parent": contract_no,"item_code":("like", f"{txt}%")},
		fields=["distinct item_code, item_name"],
		as_list=1,
	)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_project_items_list(doctype, txt, searchfield, start, page_len, filters):
	selling_price_list = filters.get("selling_price_list")
	print("==================selling_price_list=============", selling_price_list)
	# return frappe.get_all(
	# 	"Contract Items Details AL",
	# 	parent_doctype="Project",
	# 	filters={"parent": project,"item_code":("like", f"{txt}%")},
	# 	fields=["distinct item_code, item_name"],
	# 	as_list=1,
	# )
	return frappe.get_all(
		"Item Price",
		filters={"price_list": selling_price_list, "selling":1 ,"item_code":("like", f"{txt}%")},
		fields=["distinct item_code, item_name"],
		as_list=1,
	)

@frappe.whitelist()
def get_item_rate_from_contarct_type(custom_contract_no=None, item_code=None, project=None):
	print(custom_contract_no,"---custom_contract_no---",project,"---project---")
	if project:
		print("from project")
		item_rate = frappe.db.get_value("Contract Items Details AL", {"parent": project, "item_code": item_code}, 'rate')
	elif custom_contract_no :
		print("from contract")
		item_rate = frappe.db.get_value("Contract Items Details AL", {"parent": custom_contract_no, "item_code": item_code}, 'rate')
	return item_rate or 0

def set_internal_wo_reference_in_so(self, method):
		# if self.custom_work_order_no:
		# 	print(len(self.custom_work_order_no), "==========length")
		# 	work_order_no = cint(self.custom_work_order_no)
		# 	if work_order_no == 0:
		# 		frappe.throw(_("Only Digits are allowed in Work Order No."))
		# 	if len(self.custom_work_order_no) <= 15:
		# 		frappe.throw(_("Work Order No Digits need to be more than 15 Digits"))
		# 	print(work_order_no, "========work_order_no")

		# if self.custom_work_order_no and self.custom_work_order_type:
		self.custom_internal_wo_reference = cstr(self.custom_work_order_type or '') + (self.custom_work_order_no or '')

def set_cc_and_project_from_so(self, method):
	if len(self.items)>0:
		for item in self.items:
			if item.sales_order:
				cost_center, project = frappe.db.get_value("Sales Order",item.sales_order,["cost_center","project"])
				item.cost_center = cost_center
				item.project = project

def validate_contract_dates(self, method):
	if getdate(self.expected_start_date) > getdate(self.expected_end_date):
		frappe.throw(_("Expected Start Date Can't be Greater than Expected End Date."))

def validate_government_contract_no(self, method):
	print(len(self.custom_government_contract_no))
	int_contract_no = cint(self.custom_government_contract_no)
	if int_contract_no == 0:
		frappe.throw(_("Government Contract No. must have digit only"))

@frappe.whitelist()
def get_items(name):
	project_doc = frappe.get_doc("Project",name)
	item_list = frappe.db.get_all('Item', filters={"item_group": project_doc.custom_sub_item_group},fields=['name','standard_rate', 'stock_uom'])
	print("item_list=========>", item_list)
	if len(item_list)>0:
		for item in item_list:
			item_selling_price = frappe.db.get_all("Item Price",
										filters={"selling":1,"item_code":item.name},
										fields=["price_list_rate"],limit=1)
			if len(item_selling_price)>0:
				item["price_list_rate"]=item_selling_price[0].price_list_rate
	return item_list

def set_penalty_amount_in_additional_discount(self, method):
	total_penalty_amount = 0
	if len(self.items)>0:
		for item in self.items:
			if item.custom_item_penalty:
				total_penalty_amount = total_penalty_amount + item.custom_item_penalty
	
	self.discount_amount = total_penalty_amount

def set_item_qty_based_on_invoice_type(self, method):
	if self.custom_invoice_type == 'Partial Invoice' and self.is_new():
		if self.custom_percentage_qty < 1 or self.custom_percentage_qty > 100:
			frappe.throw(_("Percentage Qty must be between 0 to 100."))
		else:
			for item in self.items:
				if item.so_detail:
					so_item_qty = frappe.db.get_value("Sales Order Item",item.so_detail, 'qty')
					item.qty = (so_item_qty * self.custom_percentage_qty) / 100

def get_items_details_based_on_so_for_print_format(doc):
	table_details = frappe.db.sql(
		"""
			SELECT tsi.custom_work_order_no as work_order_no,
				tsi.custom_work_order_type as work_order_type,
				tsi.custom_work_order_description as work_order_description,
				si.custom_cost_holder as cost_holder,
				si.due_date ,
				si.total ,
				sum(tsi.amount) as amount,
				sum(tsi.custom_item_penalty) as penalty,
				sum((tsi.amount*15)/100) as tax_amt,
				coalesce(si.base_discount_amount, 0) as base_discount_amount,
				si.grand_total,
				so.total as so_total
				From `tabSales Invoice` as si 
				inner join `tabSales Invoice Item` as tsi on tsi.parent = si.name
				inner join `tabSales Order` as so on so.name = tsi.sales_order
				WHERE si.name = %s
				GROUP BY tsi.sales_order
		""",doc.name,as_dict=1,debug=1)
	# print(table_details, "-----------name")

	return table_details
