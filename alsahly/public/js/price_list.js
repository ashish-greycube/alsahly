frappe.ui.form.on("Price List", {
    setup: function (frm) {
        frm.set_query("custom_discount_account", function (doc) {
            return {
                filters: {
                    report_type: "Profit and Loss",
                    is_group: 0,
                },
            };
        })
    }
})