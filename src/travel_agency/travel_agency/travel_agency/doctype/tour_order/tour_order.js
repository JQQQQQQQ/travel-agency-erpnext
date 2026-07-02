frappe.ui.form.on("Tour Order", {
	refresh(frm) {
		frm.trigger("toggle_read_only_amounts");
	},

	order_total_amount(frm) {
		frm.trigger("calculate_amounts");
	},

	received_amount(frm) {
		frm.trigger("calculate_amounts");
	},

	refunded_amount(frm) {
		frm.trigger("calculate_amounts");
	},

	estimated_cost_amount(frm) {
		frm.trigger("calculate_amounts");
	},

	actual_cost_amount(frm) {
		frm.trigger("calculate_amounts");
	},

	paid_amount(frm) {
		frm.trigger("calculate_amounts");
	},

	calculate_amounts(frm) {
		const orderTotal = frm.doc.order_total_amount || 0;
		const received = frm.doc.received_amount || 0;
		const refunded = frm.doc.refunded_amount || 0;
		const estimatedCost = frm.doc.estimated_cost_amount || 0;
		const actualCost = frm.doc.actual_cost_amount || 0;
		const paid = frm.doc.paid_amount || 0;

		frm.set_value("pending_receipt_amount", orderTotal - received + refunded);
		frm.set_value("pending_payment_amount", actualCost - paid);
		frm.set_value("estimated_profit_amount", orderTotal - estimatedCost);
		frm.set_value("actual_profit_amount", received - actualCost);
	},

	toggle_read_only_amounts(frm) {
		[
			"pending_receipt_amount",
			"pending_payment_amount",
			"estimated_profit_amount",
			"actual_profit_amount",
		].forEach((fieldname) => frm.set_df_property(fieldname, "read_only", 1));
	},
});
