# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document


class WorkOrderTypeAL(Document):
	
	def validate(self):
		self.validate_work_order_type()
	
	def validate_work_order_type(self):
		if len(self.work_order_type)>0:
			work_order_type = cint(self.work_order_type)
			if work_order_type == 0:
				frappe.throw(_("Work Order Type must have digits only"))