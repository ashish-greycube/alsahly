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

