frappe.ui.form.on("Project", {
	setup(frm) {
        frm.trigger("hide_grid_add_row");
        
        frm.set_query("custom_main_item_group", function (doc) {
            console.log("Working")
            return {
                query: "alsahly.alsahly.doctype.contract_al.contract_al.get_main_item_group",
            };
        });

        frm.set_query("custom_sub_item_group", function (doc) {
            if (frm.doc.custom_main_item_group) {
                return {
                    filters: {
                        parent_item_group: frm.doc.custom_main_item_group,
                        is_group: 0
                    }
                };
            }
        });
	},

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.custom_items.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);
    },

    custom_fetch_items: function(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("custom_items", "");
        frappe.call({
            method: "alsahly.api.get_items",
            args: {
                "name": frm.doc.name
            },
            callback: function (r) {
                let item_list = r.message
                console.log(item_list,"item_list", "====")
                if (item_list) {
                    item_list.forEach((e) => {
                        var d = frm.add_child("custom_items");
                        frappe.model.set_value(d.doctype, d.name, 'item_code', e.name)
                        frappe.model.set_value(d.doctype, d.name, 'rate', e.standard_rate)
                        frappe.model.set_value(d.doctype, d.name, 'uom', e.stock_uom)
                        frappe.model.set_value(d.doctype, d.name, 'rate', e.price_list_rate)
                    });
                    refresh_field("custom_items");
                    frm.save()
                }
            }
        })
    }
});