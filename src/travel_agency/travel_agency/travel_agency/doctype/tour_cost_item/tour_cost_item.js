frappe.ui.form.on("Tour Cost Item", {
	tour_order(frm) {
		if (!frm.doc.tour_order) {
			return;
		}

		frappe.db.get_value("Tour Order", frm.doc.tour_order, "customer").then((response) => {
			if (response.message && response.message.customer) {
				frm.set_value("customer", response.message.customer);
			}
		});
	},

	estimated_amount(frm) {
		if (!frm.doc.actual_amount && frm.doc.estimated_amount) {
			frm.set_value("actual_amount", frm.doc.estimated_amount);
		}
	},
});
