frappe.ui.form.on("Tour Order", {
	refresh(frm) {
		frm.trigger("toggle_read_only_amounts");
		frm.trigger("add_business_buttons");
		frm.trigger("render_business_overview");
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

	add_business_buttons(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("新增费用明细"), () => {
			frappe.new_doc("Tour Cost Item", {
				tour_order: frm.doc.name,
				customer: frm.doc.customer,
			});
		}, __("业务操作"));

		frm.add_custom_button(__("新增团款流水"), () => {
			frappe.new_doc("Tour Payment Ledger", {
				tour_order: frm.doc.name,
				customer: frm.doc.customer,
			});
		}, __("业务操作"));

		frm.add_custom_button(__("新增供应商付款"), () => {
			frappe.new_doc("Supplier Payment Record", {
				tour_order: frm.doc.name,
				customer: frm.doc.customer,
			});
		}, __("业务操作"));

		frm.add_custom_button(__("查看费用明细"), () => {
			frappe.set_route("List", "Tour Cost Item", { tour_order: frm.doc.name });
		}, __("查看明细"));

		frm.add_custom_button(__("查看团款流水"), () => {
			frappe.set_route("List", "Tour Payment Ledger", { tour_order: frm.doc.name });
		}, __("查看明细"));

		frm.add_custom_button(__("查看供应商付款"), () => {
			frappe.set_route("List", "Supplier Payment Record", { tour_order: frm.doc.name });
		}, __("查看明细"));

		frm.add_custom_button(__("查看团单利润表"), () => {
			frappe.set_route("query-report", "Tour Order Profit Report", {
				customer: frm.doc.customer,
				from_date: frm.doc.departure_date,
				to_date: frm.doc.departure_date,
			});
		}, __("查看明细"));
	},

	render_business_overview(frm) {
		if (!frm.fields_dict.business_overview_html) {
			return;
		}

		const wrapper = frm.fields_dict.business_overview_html.$wrapper;
		if (frm.is_new()) {
			wrapper.html(`<div class="text-muted">${__("保存团单后可查看费用明细和团单利润。")}</div>`);
			return;
		}

		wrapper.html(`<div class="text-muted">${__("正在加载业务总览...")}</div>`);

		frappe.call({
			method:
				"travel_agency.travel_agency.doctype.tour_order.tour_order.get_tour_order_overview",
			args: {
				tour_order: frm.doc.name,
			},
			callback(response) {
				const overview = response.message || {};
				wrapper.html(build_business_overview_html(frm, overview));
			},
		});
	},
});

function build_business_overview_html(frm, overview) {
	const summary = overview.summary || {};
	const currency = summary.currency || frm.doc.currency || "CNY";
	const cards = [
		["订单总额", summary.order_total_amount],
		["已收金额", summary.received_amount],
		["待收金额", summary.pending_receipt_amount],
		["实际成本", summary.actual_cost_amount],
		["已付金额", summary.paid_amount],
		["待付金额", summary.pending_payment_amount],
		["预计毛利", summary.estimated_profit_amount],
		["实际毛利", summary.actual_profit_amount],
	];

	return `
		<div class="travel-agency-overview">
			<style>
				.travel-agency-overview .ta-card-grid {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
					gap: 10px;
					margin-bottom: 16px;
				}
				.travel-agency-overview .ta-card {
					border: 1px solid var(--border-color);
					border-radius: 8px;
					padding: 10px 12px;
					background: var(--fg-color);
				}
				.travel-agency-overview .ta-card-label {
					color: var(--text-muted);
					font-size: 12px;
					margin-bottom: 4px;
				}
				.travel-agency-overview .ta-card-value {
					font-size: 18px;
					font-weight: 600;
				}
				.travel-agency-overview .ta-section-title {
					font-weight: 600;
					margin: 18px 0 8px;
				}
				.travel-agency-overview .ta-table {
					width: 100%;
					border-collapse: collapse;
					font-size: 13px;
				}
				.travel-agency-overview .ta-table th,
				.travel-agency-overview .ta-table td {
					border: 1px solid var(--border-color);
					padding: 7px 8px;
					vertical-align: top;
				}
				.travel-agency-overview .ta-table th {
					background: var(--control-bg);
					font-weight: 600;
				}
				.travel-agency-overview .ta-empty {
					color: var(--text-muted);
					border: 1px dashed var(--border-color);
					border-radius: 8px;
					padding: 10px 12px;
				}
			</style>
			<div class="ta-card-grid">
				${cards.map(([label, value]) => render_card(label, value, currency)).join("")}
			</div>
			${render_cost_items(overview.cost_items || [], currency)}
			${render_payment_ledgers(overview.payment_ledgers || [], currency)}
			${render_supplier_payments(overview.supplier_payments || [], currency)}
		</div>
	`;
}

function render_card(label, value, currency) {
	return `
		<div class="ta-card">
			<div class="ta-card-label">${__(label)}</div>
			<div class="ta-card-value">${format_currency(value || 0, currency)}</div>
		</div>
	`;
}

function render_cost_items(rows, currency) {
	return render_table("费用明细", rows, [
		["费用日期", (row) => frappe.datetime.str_to_user(row.cost_date || "")],
		["类别", (row) => row.cost_category || ""],
		["费用名称", (row) => link_to_form("Tour Cost Item", row.name, row.cost_name || row.name)],
		["供应商", (row) => row.supplier || ""],
		["预计金额", (row) => format_currency(row.estimated_amount || 0, currency)],
		["实际金额", (row) => format_currency(row.actual_amount || 0, currency)],
		["状态", (row) => row.status || docstatus_label(row.docstatus)],
	]);
}

function render_payment_ledgers(rows, currency) {
	return render_table("团款流水", rows, [
		["日期", (row) => frappe.datetime.str_to_user(row.transaction_date || "")],
		["类型", (row) => row.transaction_type || ""],
		["类别", (row) => row.payment_category || ""],
		["金额", (row) => link_to_form("Tour Payment Ledger", row.name, format_currency(row.amount || 0, currency))],
		["方式", (row) => row.payment_method || ""],
		["财务确认", (row) => (row.finance_confirmed ? "是" : "否")],
		["状态", (row) => docstatus_label(row.docstatus)],
	]);
}

function render_supplier_payments(rows, currency) {
	return render_table("供应商付款", rows, [
		["日期", (row) => frappe.datetime.str_to_user(row.payment_date || "")],
		["供应商", (row) => row.supplier || ""],
		["类型", (row) => row.transaction_type || ""],
		["类别", (row) => row.payment_category || ""],
		["金额", (row) => link_to_form("Supplier Payment Record", row.name, format_currency(row.amount || 0, currency))],
		["方式", (row) => row.payment_method || ""],
		["财务确认", (row) => (row.finance_confirmed ? "是" : "否")],
		["状态", (row) => docstatus_label(row.docstatus)],
	]);
}

function render_table(title, rows, columns) {
	if (!rows.length) {
		return `
			<div class="ta-section-title">${__(title)}</div>
			<div class="ta-empty">${__("暂无数据")}</div>
		`;
	}

	return `
		<div class="ta-section-title">${__(title)}</div>
		<div class="table-responsive">
			<table class="ta-table">
				<thead>
					<tr>${columns.map(([label]) => `<th>${__(label)}</th>`).join("")}</tr>
				</thead>
				<tbody>
					${rows
						.map(
							(row) => `
								<tr>
									${columns.map(([, getter]) => `<td>${getter(row)}</td>`).join("")}
								</tr>
							`
						)
						.join("")}
				</tbody>
			</table>
		</div>
	`;
}

function link_to_form(doctype, name, label) {
	if (!name) {
		return escape_html(label || "");
	}
	const route = doctype.toLowerCase().replace(/\s+/g, "-");
	return `<a href="/app/${route}/${encodeURIComponent(name)}">${escape_html(label || name)}</a>`;
}

function docstatus_label(docstatus) {
	return ["草稿", "已提交", "已取消"][docstatus || 0] || "";
}

function escape_html(value) {
	return frappe.utils.escape_html(String(value ?? ""));
}
