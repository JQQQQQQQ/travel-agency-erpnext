import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


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
			return_date,
			destination,
			traveler_count,
			order_total_amount,
			received_amount,
			refunded_amount,
			pending_receipt_amount,
			estimated_cost_amount,
			actual_cost_amount,
			paid_amount,
			pending_payment_amount,
			estimated_profit_amount,
			actual_profit_amount
		from `tabTour Order`
		{where_clause}
		order by departure_date desc, modified desc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row.net_received_amount = flt(row.received_amount) - flt(row.refunded_amount)
		row.actual_profit_margin = (
			flt(row.actual_profit_amount) / flt(row.order_total_amount) * 100
			if flt(row.order_total_amount)
			else 0
		)

	return rows


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
		{"label": _("出发日期"), "fieldname": "departure_date", "fieldtype": "Date", "width": 100},
		{"label": _("返程日期"), "fieldname": "return_date", "fieldtype": "Date", "width": 100},
		{"label": _("目的地"), "fieldname": "destination", "fieldtype": "Data", "width": 120},
		{"label": _("人数"), "fieldname": "traveler_count", "fieldtype": "Int", "width": 80},
		{"label": _("订单总额"), "fieldname": "order_total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("已收金额"), "fieldname": "received_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("已退款"), "fieldname": "refunded_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("净收款"), "fieldname": "net_received_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("待收金额"), "fieldname": "pending_receipt_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("预计成本"), "fieldname": "estimated_cost_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("实际成本"), "fieldname": "actual_cost_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("已付金额"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("待付金额"), "fieldname": "pending_payment_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("预计毛利"), "fieldname": "estimated_profit_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("实际毛利"), "fieldname": "actual_profit_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("实际毛利率%"), "fieldname": "actual_profit_margin", "fieldtype": "Percent", "width": 110},
	]


def get_chart(data):
	total_order_amount = sum(flt(row.order_total_amount) for row in data)
	total_actual_cost = sum(flt(row.actual_cost_amount) for row in data)
	total_actual_profit = sum(flt(row.actual_profit_amount) for row in data)

	return {
		"data": {
			"labels": [_("订单总额"), _("实际成本"), _("实际毛利")],
			"datasets": [{"values": [total_order_amount, total_actual_cost, total_actual_profit]}],
		},
		"type": "bar",
		"height": 280,
	}
