frappe.ui.form.on("Sales Invoice", {

	custom_per_item_penalty(frm) {
        if ((frm.doc.items).length > 0) {
            for( let row of frm.doc.items ) {
                if (row.custom_item_penalty == 0 || row.custom_item_penalty == null) {
                    frappe.model.set_value(row.doctype, row.name, "custom_item_penalty", frm.doc.custom_per_item_penalty);
                }
            }
        }
	},
});

frappe.ui.form.on("Sales Invoice Item", {
    items_add(doc, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if (cur_frm.doc.custom_per_item_penalty) {
			row.custom_item_penalty = cur_frm.doc.custom_per_item_penalty;
			refresh_field("custom_item_penalty", cdn, "items");
		} 
        else {
			cur_frm.script_manager.copy_from_first_row("items", row, ["custom_item_penalty"]);
		}
	},
});