frappe.listview_settings["Tour Order"] = {
	add_fields: [
		"order_status",
		"departure_date",
		"destination",
		"order_total_amount",
		"pending_receipt_amount",
		"pending_payment_amount",
		"actual_profit_amount",
	],

	get_indicator(doc) {
		if (doc.order_status === "已取消") {
			return [__("已取消"), "red", "order_status,=,已取消"];
		}

		if (flt(doc.pending_receipt_amount) > 0) {
			return [__("待收款"), "orange", "pending_receipt_amount,>,0"];
		}

		if (flt(doc.pending_payment_amount) > 0) {
			return [__("待付款"), "blue", "pending_payment_amount,>,0"];
		}

		if (doc.order_status === "已完团" || doc.order_status === "已收清") {
			return [__(doc.order_status), "green", `order_status,=,${doc.order_status}`];
		}

		return [__(doc.order_status || "待确认"), "gray", `order_status,=,${doc.order_status || "待确认"}`];
	},

	onload(listview) {
		listview.page.add_inner_button(__("待收款"), () => {
			listview.filter_area.add("Tour Order", "pending_receipt_amount", ">", 0);
		});

		listview.page.add_inner_button(__("待付款"), () => {
			listview.filter_area.add("Tour Order", "pending_payment_amount", ">", 0);
		});

		listview.page.add_inner_button(__("即将出团"), () => {
			const today = frappe.datetime.get_today();
			const nextWeek = frappe.datetime.add_days(today, 7);
			listview.filter_area.add([
				["Tour Order", "departure_date", ">=", today],
				["Tour Order", "departure_date", "<=", nextWeek],
				["Tour Order", "order_status", "!=", "已取消"],
			]);
		});

		listview.page.add_inner_button(__("清除筛选"), () => {
			listview.filter_area.clear();
		});
	},
};
