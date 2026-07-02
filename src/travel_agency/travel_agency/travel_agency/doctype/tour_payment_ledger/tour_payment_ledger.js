frappe.ui.form.on("Tour Payment Ledger", {
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

	transaction_type(frm) {
		if (frm.doc.transaction_type === "退款") {
			frm.set_value("payment_category", "退款");
		}
	},
});
