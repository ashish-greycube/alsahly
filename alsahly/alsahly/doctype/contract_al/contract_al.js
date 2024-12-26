// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract AL", {
	setup(frm) {
        frm.trigger("hide_grid_add_row");
        
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

        // frm.set_query("item_code", "items", function (doc) {
        //     if (frm.doc.sub_item_group) {
        //         return {
        //             filters: {
        //                 item_group: frm.doc.sub_item_group,
        //             }
        //         };
        //     }
        // })
	},

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.items.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);
    },

    fetch_items: function(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("items", "");
        frm.call({
            doc: frm.doc,
            method: "get_items",
            freeze: true,
            callback: (r) => {
                let item_list = r.message
                console.log(item_list,"item_list", "====")
                if (item_list) {
                    item_list.forEach((e) => {
                        var d = frm.add_child("items");
                        frappe.model.set_value(d.doctype, d.name, 'item_code', e.name)
                        frappe.model.set_value(d.doctype, d.name, 'rate', e.standard_rate)
                        frappe.model.set_value(d.doctype, d.name, 'uom', e.stock_uom)
                        frappe.model.set_value(d.doctype, d.name, 'rate', e.price_list_rate)
                    });
                    refresh_field("items");
                    frm.save()
                }
            },
        });
    }
});
