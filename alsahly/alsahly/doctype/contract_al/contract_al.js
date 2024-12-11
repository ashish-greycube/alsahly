// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract AL", {
	setup(frm) {
        frm.set_query("main_item_group", function (doc) {
            console.log("Working")
            return {
                query: "alsahly.alsahly.doctype.contract_al.contract_al.get_main_item_group",
            };
        });

        frm.set_query("sub_item_group", function (doc) {
            if (frm.doc.main_item_group) {
                return {
                    filters: {
                        parent_item_group: frm.doc.main_item_group,
                        is_group: 0
                    }
                };
            }
        });

        frm.set_query("item_code", "items", function (doc) {
            if (frm.doc.sub_item_group) {
                return {
                    filters: {
                        item_group: frm.doc.sub_item_group,
                    }
                };
            }
        })
	}
});


frappe.ui.form.on("Contract Items Details AL", {
    item_code: function(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        frappe.call({
            method: "alsahly.alsahly.doctype.contract_al.contract_al.get_item_code_details",
            args: {
                item_code: row.item_code,
            },
            callback: function (r) {
                console.log(r.message)
                frappe.model.set_value(cdt, cdn, 'rate', r.message.standard_rate)
                frappe.model.set_value(cdt, cdn, 'uom', r.message.stock_uom)
            }
        })
    }
})