import frappe 
from frappe import _

def get_final_part_invoice_template_data(item_table, doc):
    data = []
    if len(item_table) > 0:
        for item in item_table:
            row = {
                'work_order_no' : item.custom_work_order_no,
                'work_order_type' : item.custom_work_order_type,
                'work_order_description' : item.custom_work_order_description,
                'cost_holder' : item.custom_cost_holder,
                'achievment_date' : doc.due_date,
                'total_order_amnt' : frappe.db.get_value("Sales Order Item", {'parent': item.sales_order, 'item_code': item.item_code}, 'amount') or 0,
                'total_billed_amnt' :  frappe.db.get_value("Sales Order Item", {'parent': item.sales_order, 'item_code': item.item_code}, 'billed_amt') or 0,
                'total_amnt_before_discount' : item.price_list_rate * item.qty,
                'discount_amnt' : item.discount_amount * item.qty,
                'custom_item_discount_amount': item.custom_item_discount_amount,
                'final_taxable_amnt' : item.amount,
                'tax' : '15%',
                'tax_amnt' : item.amount * 0.15,
                'penalty_amnt' : item.custom_item_penalty,
                'total_included_tax' : item.amount + (item.amount * 0.15),
            }
            data.append(row)

        work_order_no_wise_sorted_data = []
       
        for d in data:
            isFound = False
            if len(work_order_no_wise_sorted_data) > 0:
                for sd in work_order_no_wise_sorted_data:
                    if sd['work_order_no'] == d['work_order_no']:
                        isFound = True
                        sd.update({
                                "total_order_amnt" : sd['total_order_amnt'] + d['total_order_amnt'],
                                "total_billed_amnt" : sd['total_billed_amnt'] + d['total_billed_amnt'],
                                "total_amnt_before_discount" : sd['total_amnt_before_discount'] + d['total_amnt_before_discount'],
                                "discount_amnt" : sd['discount_amnt'] + d['discount_amnt'],
                                "custom_item_discount_amount" : sd['custom_item_discount_amount'] + d['custom_item_discount_amount'],
                                "final_taxable_amnt" : sd['final_taxable_amnt'] + d['final_taxable_amnt'],
                                "tax_amnt" : sd['tax_amnt'] + d['tax_amnt'],
                                "penalty_amnt" : sd['penalty_amnt'] + d['penalty_amnt'],
                                "total_included_tax" : sd['total_included_tax'] + d['total_included_tax']
                        })

                    
            if isFound == False:
                row = {
                    'work_order_no' : d['work_order_no'],
                    'work_order_type' : d['work_order_type'],
                    'work_order_description' : d['work_order_description'],
                    'cost_holder' : d['cost_holder'],
                    'achievment_date' : d['achievment_date'],
                    'total_order_amnt' : d['total_order_amnt'],
                    'total_billed_amnt' :  d['total_billed_amnt'],
                    'total_amnt_before_discount' : d['total_amnt_before_discount'],
                    'discount_amnt' : d['discount_amnt'],
                    'custom_item_discount_amount': d['custom_item_discount_amount'],
                    'final_taxable_amnt' : d['final_taxable_amnt'],
                    'tax' : '15%',
                    'tax_amnt' : d['tax_amnt'],
                    'penalty_amnt' : d['penalty_amnt'],
                    'total_included_tax' : d['total_included_tax'],

                }
                work_order_no_wise_sorted_data.append(row)

        return work_order_no_wise_sorted_data


def get_payment_entry_data(sales_invoice, total_invoiced):
    data = []
    if sales_invoice != None:
        pes = frappe.db.get_all(
            "Payment Entry Reference",
            filters = {
                "reference_name" : sales_invoice
            },
            fields = ['parent']
        )
        print(pes)
        if len(pes) > 0:
            total_amount = 0
            for pe in pes:
                doc = frappe.get_doc("Payment Entry", pe['parent'])
                row = {
                    'rowname' : "{0}-{1}-{2}".format(_(doc.mode_of_payment), doc.name,doc.posting_date,),
                    'amount' : doc.total_allocated_amount,
                    'date' : doc.posting_date
                }
                total_amount = total_amount +  doc.total_allocated_amount
                data.append(row)
                print(data)
            # total_row = {
            #     'rowname' : _('Outstanding Invoiced Amount'),
            #     'amount' : total_invoiced - total_amount
            # }
            # data.append(total_row)
            return data
        
def get_returned_si_amount(sales_invoice):
    returned_si = frappe.db.get_list("Sales Invoice", filters={"is_return":1, "return_against": sales_invoice, "docstatus":1}, fields=["name"])
    si_doc = frappe.get_doc("Sales Invoice", sales_invoice)
    return_data = []
    if len(returned_si) > 0:
        for si in returned_si:
            doc = frappe.get_doc("Sales Invoice", si['name'])
            row = {
                'rowname' : "{0}-{1}-{2}".format(("إشعار دائن"),doc.name, doc.posting_date,),
                'amount' : doc.grand_total + si_doc.grand_total,
                'date' : doc.posting_date
            }
            return_data.append(row)
        return return_data
    
def get_journal_entry_data(sales_invoice):
    data = []
    if sales_invoice != None:
        jes = frappe.db.get_all("Journal Entry Account", filters = {'reference_type' : 'Sales Invoice', 'reference_name':sales_invoice}, fields = ['parent'])
        print(jes)
        if len(jes) > 0:
            for je in jes:
                doc = frappe.get_doc("Journal Entry", je['parent'])
                row = {
                    'rowname' : "{0}-{1}-{2}".format(("قيد يومية"), doc.name, doc.posting_date),
                    'amount' : doc.total_debit,
                    'date' : doc.posting_date
                }
                data.append(row)
            return data
        
def get_ordered_deduction_data(pe_data, re_data, je_data):
    ordered_data = []
    ordered_dates = []
    
    for pe in pe_data:
        if pe.get('date') not in ordered_dates:
            ordered_dates.append(pe.get('date'))
    for re in re_data:
        if re.get('date') not in ordered_dates:
            ordered_dates.append(re.get('date'))
    for je in je_data:
        if je.get('date') not in ordered_dates:
            ordered_dates.append(je.get('date'))
   
    ordered_dates = sorted(ordered_dates)
   
    for od in ordered_dates:
        for pe in pe_data:
            if pe.get('date') == od:
                ordered_data.append(pe)
        for re in re_data:
            if re.get('date') == od:
                ordered_data.append(re)
        for je in je_data:
            if je.get('date') == od:
                ordered_data.append(je)
    
    return ordered_data