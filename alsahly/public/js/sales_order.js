frappe.ui.form.on("Sales Order", {
    setup: function(frm){
        frm.set_query("custom_contract_no", function (doc) {
            return {
				filters: {
					customer_name: frm.doc.customer
				}
			}
        })
    },

    onload_post_render: function(frm) {
        console.log("Helloooo")
        frm.set_query("item_code", "items", function (doc, cdt, cdn) {
            // let row = locals[cdt][cdn];
            if (doc.custom_contract_no) {
                return {
                    query: "alsahly.api.get_contract_items_list",
                    filters: {
                        contract_no: frm.doc.custom_contract_no
                    },
                };
            }
            else{
                return {
                    filters: {
                        is_sales_item: 1,
                        has_variants: 0
                    }
                }
            }
        });
    },
})

frappe.ui.form.on("Sales Order Item", {
    item_code: function (frm, cdt, cdn) {
        setTimeout(() => {
            let row = locals[cdt][cdn];
            frappe.call({
                method: "alsahly.api.get_item_rate_from_contarct_type",
                args: {
                    custom_contract_no: frm.doc.custom_contract_no,
                    item_code: row.item_code,
                },
                callback: function (r) {
                    console.log(r.message)
                    frappe.model.set_value(cdt, cdn, 'rate', r.message)
                    frappe.show_alert({ message: __("Item Rate Set From Contract Type."), indicator: "green" }, 1);
                }
            })
        }, 550)
    }
})