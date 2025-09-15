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

	custom_per_item_penalty(frm) {
        if ((frm.doc.items).length > 0) {
            for( let row of frm.doc.items ) {
                if (row.custom_item_penalty == 0 || row.custom_item_penalty == null) {
                    frappe.model.set_value(row.doctype, row.name, "custom_item_penalty", frm.doc.custom_per_item_penalty);
                }
            }
        }
	},

    project(frm){
        let project = frm.doc.project
        frappe.db.get_value('Project', project , 'custom_price_list')
            .then(r => {
            console.log(r.message.custom_price_list)
            frm.set_value('selling_price_list', r.message.custom_price_list)
        })
    },

    onload_post_render: function(frm) {
        console.log("Helloooo")
        frm.set_query("item_code", "items", function (doc, cdt, cdn) {
            // let row = locals[cdt][cdn];
            if (doc.selling_price_list) {
                return {
                    query: "alsahly.api.get_project_items_list",
                    filters: {
                        selling_price_list: frm.doc.selling_price_list
                    },
                };
            }
            // else if (doc.custom_contract_no) {
            //     return {
            //         query: "alsahly.api.get_contract_items_list",
            //         filters: {
            //             contract_no: frm.doc.custom_contract_no
            //         },
            //     };
            // }
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

    custom_cost_holder: function(frm) {
        set_cost_holder_in_item_table(frm)
    }
})

frappe.ui.form.on("Sales Order Item", {
    items_add(doc, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
        console.log(cur_frm.doc.custom_per_item_penalty,"doc.custom_per_item_penalty")
		if (cur_frm.doc.custom_per_item_penalty) {
			row.custom_item_penalty = cur_frm.doc.custom_per_item_penalty;
			refresh_field("custom_item_penalty", cdn, "items");
		} 
        else {
			cur_frm.script_manager.copy_from_first_row("items", row, ["custom_item_penalty"]);
		}

        if (cur_frm.doc.custom_cost_holder && cur_frm.doc.custom_cost_holder != "Both"){
            frappe.model.set_value(cdt, cdn, "custom_cost_holder", cur_frm.doc.custom_cost_holder)
        }
	},
});

let set_cost_holder_in_item_table = function(frm){
    if (frm.doc.custom_cost_holder && frm.doc.items.length > 0 && frm.doc.custom_cost_holder != "Both") {
        frm.doc.items.forEach(item => {
            frappe.model.set_value(item.doctype, item.name, "custom_cost_holder", frm.doc.custom_cost_holder)
        });
    }
    else {
        frm.doc.items.forEach(item => {
            frappe.model.set_value(item.doctype, item.name, "custom_cost_holder", '')
        })
    }
}