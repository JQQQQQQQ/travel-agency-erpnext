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
				bind_business_overview_actions(frm, wrapper);
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
				.travel-agency-overview .ta-inline-forms {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
					gap: 10px;
					margin-bottom: 14px;
				}
				.travel-agency-overview .ta-inline-form {
					border: 1px solid var(--border-color);
					border-radius: 8px;
					background: var(--fg-color);
					padding: 10px 12px;
				}
				.travel-agency-overview .ta-inline-form summary {
					cursor: pointer;
					font-weight: 600;
				}
				.travel-agency-overview .ta-form-grid {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
					gap: 8px;
					margin-top: 10px;
				}
				.travel-agency-overview .ta-form-field span {
					display: block;
					color: var(--text-muted);
					font-size: 12px;
					margin-bottom: 4px;
				}
				.travel-agency-overview .ta-form-actions {
					display: flex;
					align-items: end;
				}
			</style>
			<div class="ta-card-grid">
				${cards.map(([label, value]) => render_card(label, value, currency)).join("")}
			</div>
			${render_inline_forms()}
			${render_cost_items(overview.cost_items || [], currency)}
			${render_payment_ledgers(overview.payment_ledgers || [], currency)}
			${render_supplier_payments(overview.supplier_payments || [], currency)}
		</div>
	`;
}

function render_inline_forms() {
	const today = frappe.datetime.get_today();
	return `
		<div class="ta-section-title">${__("直接新增明细")}</div>
		<div class="ta-inline-forms">
			<details class="ta-inline-form">
				<summary>${__("新增费用明细")}</summary>
				<div class="ta-form-grid" data-section="cost">
					${select_field("费用类别", "cost_category", ["酒店", "车队", "门票", "导游", "餐费", "机票", "火车票", "签证", "保险", "地接", "其他"])}
					${input_field("费用名称", "cost_name", "text", "例如：桂林地接服务")}
					${input_field("供应商", "supplier", "text", "填写系统中的供应商名称")}
					${input_field("预计金额", "estimated_amount", "number")}
					${input_field("实际金额", "actual_amount", "number")}
					${input_field("费用日期", "cost_date", "date", "", today)}
					<div class="ta-form-actions">
						<button class="btn btn-primary btn-sm" data-action="save-cost">${__("保存费用明细")}</button>
					</div>
				</div>
			</details>
			<details class="ta-inline-form">
				<summary>${__("新增团款流水")}</summary>
				<div class="ta-form-grid" data-section="payment">
					${select_field("流水类型", "transaction_type", ["收款", "退款"])}
					${select_field("收款类别", "payment_category", ["定金", "尾款", "补款", "退款", "其他"])}
					${input_field("金额", "amount", "number")}
					${input_field("日期", "transaction_date", "date", "", today)}
					${select_field("收付方式", "payment_method", ["微信", "支付宝", "现金", "银行卡", "对公转账", "其他"])}
					<div class="ta-form-actions">
						<button class="btn btn-primary btn-sm" data-action="save-payment">${__("保存团款流水")}</button>
					</div>
				</div>
			</details>
			<details class="ta-inline-form">
				<summary>${__("新增供应商付款")}</summary>
				<div class="ta-form-grid" data-section="supplier-payment">
					${input_field("供应商", "supplier", "text", "填写系统中的供应商名称")}
					${select_field("流水类型", "transaction_type", ["付款", "退款"])}
					${select_field("付款类别", "payment_category", ["预付款", "尾款", "补款", "退款", "其他"])}
					${input_field("金额", "amount", "number")}
					${input_field("付款日期", "payment_date", "date", "", today)}
					${select_field("付款方式", "payment_method", ["微信", "支付宝", "现金", "银行卡", "对公转账", "其他"])}
					<div class="ta-form-actions">
						<button class="btn btn-primary btn-sm" data-action="save-supplier-payment">${__("保存供应商付款")}</button>
					</div>
				</div>
			</details>
		</div>
	`;
}

function input_field(label, fieldname, type, placeholder = "", value = "") {
	return `
		<label class="ta-form-field">
			<span>${__(label)}</span>
			<input
				class="form-control"
				data-field="${fieldname}"
				type="${type}"
				placeholder="${escape_html(placeholder)}"
				value="${escape_html(value)}"
			/>
		</label>
	`;
}

function select_field(label, fieldname, options) {
	return `
		<label class="ta-form-field">
			<span>${__(label)}</span>
			<select class="form-control" data-field="${fieldname}">
				${options.map((option) => `<option value="${escape_html(option)}">${__(option)}</option>`).join("")}
			</select>
		</label>
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

function bind_business_overview_actions(frm, wrapper) {
	wrapper.find("[data-action='save-cost']").on("click", () => {
		const values = get_inline_values(wrapper, "cost");
		if (!values.cost_category || !values.cost_name) {
			frappe.msgprint(__("请填写费用类别和费用名称"));
			return;
		}
		save_overview_detail(frm, {
			method:
				"travel_agency.travel_agency.doctype.tour_order.tour_order.add_cost_item_from_overview",
			args: {
				tour_order: frm.doc.name,
				cost_category: values.cost_category,
				cost_name: values.cost_name,
				supplier: values.supplier,
				estimated_amount: values.estimated_amount,
				actual_amount: values.actual_amount,
				cost_date: values.cost_date,
			},
			success_message: __("费用明细已保存"),
		});
	});

	wrapper.find("[data-action='save-payment']").on("click", () => {
		const values = get_inline_values(wrapper, "payment");
		if (!values.amount || Number(values.amount) <= 0) {
			frappe.msgprint(__("请填写大于 0 的团款金额"));
			return;
		}
		save_overview_detail(frm, {
			method:
				"travel_agency.travel_agency.doctype.tour_order.tour_order.add_payment_ledger_from_overview",
			args: {
				tour_order: frm.doc.name,
				transaction_type: values.transaction_type,
				payment_category: values.payment_category,
				amount: values.amount,
				transaction_date: values.transaction_date,
				payment_method: values.payment_method,
			},
			success_message: __("团款流水已保存"),
		});
	});

	wrapper.find("[data-action='save-supplier-payment']").on("click", () => {
		const values = get_inline_values(wrapper, "supplier-payment");
		if (!values.supplier) {
			frappe.msgprint(__("请填写供应商"));
			return;
		}
		if (!values.amount || Number(values.amount) <= 0) {
			frappe.msgprint(__("请填写大于 0 的付款金额"));
			return;
		}
		save_overview_detail(frm, {
			method:
				"travel_agency.travel_agency.doctype.tour_order.tour_order.add_supplier_payment_from_overview",
			args: {
				tour_order: frm.doc.name,
				supplier: values.supplier,
				transaction_type: values.transaction_type,
				payment_category: values.payment_category,
				amount: values.amount,
				payment_date: values.payment_date,
				payment_method: values.payment_method,
			},
			success_message: __("供应商付款已保存"),
		});
	});
}

function get_inline_values(wrapper, section) {
	const container = wrapper.find(`[data-section='${section}']`);
	const values = {};
	container.find("[data-field]").each((index, element) => {
		const field = $(element);
		values[field.attr("data-field")] = field.val();
	});
	return values;
}

function save_overview_detail(frm, options) {
	frappe.call({
		method: options.method,
		args: options.args,
		freeze: true,
		freeze_message: __("正在保存..."),
		callback(response) {
			if (response.exc) {
				return;
			}
			frappe.show_alert({ message: options.success_message, indicator: "green" });
			frm.reload_doc();
		},
	});
}
