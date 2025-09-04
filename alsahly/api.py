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
				print("==========set_cc_and_project_from_so===============")

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
				print(item.custom_item_penalty)
				total_penalty_amount = total_penalty_amount + item.custom_item_penalty
	print(total_penalty_amount)

	if self.doctype == "Sales Invoice":
		self.custom_original_penalty = total_penalty_amount
		self.discount_amount = self.custom_original_penalty + (self.custom_extra_penalty or 0)
	elif self.doctype == "Sales Order":
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
				sum(tsi.discount_amount) as discount_amount,
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

def validate_penalty_percentage(self, method):
	if self.custom_penalty_type == "Percentage":
		if self.custom_item_penalty <= 0:
			frappe.throw(_("Item Penalty Percentage must be between 0 to 100"))
	if self.custom_penalty_type == "Amount":
		if self.custom_item_penalty <= 0:
			frappe.throw(_("Item Penalty must be greater than 0"))

def set_penalty_amount_in_child_based_on_type(self, method):
	total_amount = 0
	if len(self.items)>0:
		for row in self.items:
			if self.custom_before_discount == 1:
				before_discount_amount = row.qty * row.price_list_rate
				total_amount = total_amount + before_discount_amount
			else :
				total_amount = total_amount + row.amount
	print(total_amount,"total")
	per_item_penaty = 0
	for ele in self.items:
		if self.custom_penalty_type == "Amount":
			if self.custom_before_discount == 1:
				per_item_penaty = (self.custom_item_penalty * ele.qty * ele.price_list_rate) / total_amount
				print(per_item_penaty,"before")
			else :
				per_item_penaty = (self.custom_item_penalty * ele.amount ) / total_amount
				print(per_item_penaty, "after")
		elif self.custom_penalty_type == "Percentage":
			if self.custom_before_discount == 1:
				per_item_penaty = (self.custom_item_penalty * ele.qty * ele.price_list_rate) / 100
			else :
				per_item_penaty = (self.custom_item_penalty * ele.amount ) / 100
		elif self.custom_penalty_type == "Manual":
			per_item_penaty = ele.custom_item_penalty
		ele.custom_item_penalty = per_item_penaty


def set_workorder_selection_in_si(self, method):
	if len(self.items) > 0:
		unique_so_ref = []
		for item in self.items:
			if item.sales_order and item.sales_order not in unique_so_ref:
				unique_so_ref.append(item.sales_order)

		if len(unique_so_ref) > 1:
			self.custom_cost_holder = ""
			self.custom_work_order_type = ""
			self.custom_work_order_type_description = ""
			self.custom_work_order_no = ""
			self.custom_internal_wo_reference = ""

		elif len(unique_so_ref) == 1:
			so = frappe.db.get_value('Sales Order', unique_so_ref[0], ['custom_cost_holder', 'custom_work_order_type', 'custom_work_order_type_description', 'custom_work_order_no', 'custom_internal_wo_reference'], as_dict=1)

			self.custom_cost_holder = so.custom_cost_holder or ''
			self.custom_work_order_type = so.custom_work_order_type or ''
			self.custom_work_order_type_description = so.custom_work_order_type_description or ''
			self.custom_work_order_no = so.custom_work_order_no or ''
			self.custom_internal_wo_reference = so.custom_internal_wo_reference or ''

		else:
			pass

def set_discount_account_from_so_price_list_in_si(self, method):
	if len(self.items) > 0:
		for item in self.items:
			if item.sales_order :
				price_list = frappe.db.get_value("Sales Order", item.sales_order, "selling_price_list")
				if price_list:
					discount_acc = frappe.db.get_value("Price List", price_list, "custom_discount_account")
					item.discount_account = discount_acc or ''
					# print(item.discount_account, "===================discount_account=============")

def set_cost_holder_in_si(self, method):
	if len(self.items) > 0:
		for item in self.items:
			if item.sales_order:
				cost_holder = frappe.db.get_value("Sales Order", item.sales_order, "custom_cost_holder")
				item.custom_cost_holder = cost_holder