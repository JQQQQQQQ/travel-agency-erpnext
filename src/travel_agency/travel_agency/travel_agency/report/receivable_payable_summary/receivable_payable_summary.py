import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	report_summary = get_report_summary(data)
	chart = get_chart(data)
	return columns, data, None, chart, report_summary


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("departure_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions.append("departure_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters.get("customer")

	if filters.get("order_status"):
		conditions.append("order_status = %(order_status)s")
		values["order_status"] = filters.get("order_status")

	if filters.get("only_pending"):
		conditions.append("(pending_receipt_amount != 0 or pending_payment_amount != 0)")

	where_clause = " and ".join(conditions)
	if where_clause:
		where_clause = f"where {where_clause}"

	rows = frappe.db.sql(
		f"""
		select
			name as tour_order,
			tour_order_name,
			customer,
			order_status,
			departure_date,
			destination,
			order_total_amount,
			received_amount,
			refunded_amount,
			pending_receipt_amount,
			actual_cost_amount,
			paid_amount,
			pending_payment_amount,
			actual_profit_amount
		from `tabTour Order`
		{where_clause}
		order by greatest(abs(pending_receipt_amount), abs(pending_payment_amount)) desc, departure_date desc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row.net_received_amount = flt(row.received_amount) - flt(row.refunded_amount)
		row.cash_gap_amount = flt(row.pending_receipt_amount) - flt(row.pending_payment_amount)
		row.risk_status = get_risk_status(row)

	return rows


def get_risk_status(row):
	if flt(row.pending_receipt_amount) > 0 and flt(row.pending_payment_amount) > 0:
		return "待收待付"
	if flt(row.pending_receipt_amount) > 0:
		return "待收款"
	if flt(row.pending_payment_amount) > 0:
		return "待付款"
	return "已结清"


def get_columns():
	return [
		{
			"label": _("团单"),
			"fieldname": "tour_order",
			"fieldtype": "Link",
			"options": "Tour Order",
			"width": 150,
		},
		{"label": _("团单名称"), "fieldname": "tour_order_name", "fieldtype": "Data", "width": 180},
		{
			"label": _("客户"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{"label": _("状态"), "fieldname": "order_status", "fieldtype": "Data", "width": 100},
		{"label": _("风险状态"), "fieldname": "risk_status", "fieldtype": "Data", "width": 100},
		{"label": _("出发日期"), "fieldname": "departure_date", "fieldtype": "Date", "width": 100},
		{"label": _("目的地"), "fieldname": "destination", "fieldtype": "Data", "width": 120},
		{"label": _("订单总额"), "fieldname": "order_total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("已收金额"), "fieldname": "received_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("已退款"), "fieldname": "refunded_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("净收款"), "fieldname": "net_received_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("待收金额"), "fieldname": "pending_receipt_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("实际成本"), "fieldname": "actual_cost_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("已付金额"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("待付金额"), "fieldname": "pending_payment_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("现金缺口"), "fieldname": "cash_gap_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("实际毛利"), "fieldname": "actual_profit_amount", "fieldtype": "Currency", "width": 120},
	]


def get_report_summary(data):
	total_pending_receipt = sum(flt(row.pending_receipt_amount) for row in data)
	total_pending_payment = sum(flt(row.pending_payment_amount) for row in data)
	total_cash_gap = total_pending_receipt - total_pending_payment
	total_profit = sum(flt(row.actual_profit_amount) for row in data)

	return [
		{"value": total_pending_receipt, "label": _("待收总额"), "datatype": "Currency"},
		{"value": total_pending_payment, "label": _("待付总额"), "datatype": "Currency"},
		{"value": total_cash_gap, "label": _("现金缺口"), "datatype": "Currency"},
		{"value": total_profit, "label": _("实际毛利"), "datatype": "Currency"},
	]


def get_chart(data):
	total_pending_receipt = sum(flt(row.pending_receipt_amount) for row in data)
	total_pending_payment = sum(flt(row.pending_payment_amount) for row in data)

	return {
		"data": {
			"labels": [_("待收金额"), _("待付金额")],
			"datasets": [{"values": [total_pending_receipt, total_pending_payment]}],
		},
		"type": "donut",
		"height": 280,
	}
