frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		hide_work_order_section_for_multiple_so_ref(frm)
	},

	// custom_per_item_penalty(frm) {
    //     if ((frm.doc.items).length > 0) {
    //         for( let row of frm.doc.items ) {
    //             if (row.custom_item_penalty == 0 || row.custom_item_penalty == null) {
    //                 frappe.model.set_value(row.doctype, row.name, "custom_item_penalty", frm.doc.custom_per_item_penalty);
    //             }
    //         }
    //     }
	// },
});

frappe.ui.form.on("Sales Invoice Item", {
    // items_add(doc, cdt, cdn) {
	// 	var row = frappe.get_doc(cdt, cdn);
	// 	if (cur_frm.doc.custom_per_item_penalty) {
	// 		row.custom_item_penalty = cur_frm.doc.custom_per_item_penalty;
	// 		refresh_field("custom_item_penalty", cdn, "items");
	// 	} 
    //     else {
	// 		cur_frm.script_manager.copy_from_first_row("items", row, ["custom_item_penalty"]);
	// 	}
	// },
});

let hide_work_order_section_for_multiple_so_ref = function (frm) {
	let unique_so = []
	frm.doc.items.forEach(e => {
		if (e.sales_order && !unique_so.includes(e.sales_order)){
			unique_so.push(e.sales_order)
		}
	});
	if (unique_so.length > 1){
		frm.set_df_property("custom_section_break_kql4p", "hidden", 1)
	}
	else if (unique_so.length == 1){
		frm.set_df_property("custom_section_break_kql4p", "hidden", 0)
	}
}