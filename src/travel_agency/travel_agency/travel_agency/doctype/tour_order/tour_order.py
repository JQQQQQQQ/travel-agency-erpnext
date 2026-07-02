import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class TourOrder(Document):
	def validate(self):
		self.set_missing_amounts()
		self.validate_dates()
		self.calculate_amounts()

	def set_missing_amounts(self):
		for fieldname in (
			"received_amount",
			"refunded_amount",
			"pending_receipt_amount",
			"estimated_cost_amount",
			"actual_cost_amount",
			"paid_amount",
			"pending_payment_amount",
			"estimated_profit_amount",
			"actual_profit_amount",
		):
			if self.get(fieldname) is None:
				self.set(fieldname, 0)

	def validate_dates(self):
		if self.return_date and self.departure_date and self.return_date < self.departure_date:
			frappe.throw("返程日期不能早于出发日期")

	def calculate_amounts(self):
		order_total = self.order_total_amount or 0
		received = self.received_amount or 0
		refunded = self.refunded_amount or 0
		estimated_cost = self.estimated_cost_amount or 0
		actual_cost = self.actual_cost_amount or 0
		paid = self.paid_amount or 0

		self.pending_receipt_amount = order_total - received + refunded
		self.pending_payment_amount = actual_cost - paid
		self.estimated_profit_amount = order_total - estimated_cost
		self.actual_profit_amount = received - actual_cost

	def recompute_payment_totals(self):
		row = frappe.db.sql(
			"""
			select
				sum(case when transaction_type = '收款' then amount else 0 end) as received_amount,
				sum(case when transaction_type = '退款' then amount else 0 end) as refunded_amount
			from `tabTour Payment Ledger`
			where tour_order = %s and docstatus = 1
			""",
			self.name,
			as_dict=True,
		)[0]

		self.received_amount = row.received_amount or 0
		self.refunded_amount = row.refunded_amount or 0
		self.calculate_amounts()
		self.db_update()

	def recompute_cost_totals(self):
		row = frappe.db.sql(
			"""
			select
				sum(estimated_amount) as estimated_cost_amount,
				sum(actual_amount) as actual_cost_amount
			from `tabTour Cost Item`
			where tour_order = %s and docstatus = 1
			""",
			self.name,
			as_dict=True,
		)[0]

		self.estimated_cost_amount = row.estimated_cost_amount or 0
		self.actual_cost_amount = row.actual_cost_amount or 0
		self.calculate_amounts()
		self.db_update()

	def recompute_supplier_payment_totals(self):
		row = frappe.db.sql(
			"""
			select
				sum(case when transaction_type = '付款' then amount else 0 end) as paid_amount,
				sum(case when transaction_type = '退款' then amount else 0 end) as supplier_refund_amount
			from `tabSupplier Payment Record`
			where tour_order = %s and docstatus = 1
			""",
			self.name,
			as_dict=True,
		)[0]

		self.paid_amount = (row.paid_amount or 0) - (row.supplier_refund_amount or 0)
		self.calculate_amounts()
		self.db_update()


@frappe.whitelist()
def get_tour_order_overview(tour_order):
	doc = frappe.get_doc("Tour Order", tour_order)
	doc.check_permission("read")

	return {
		"summary": {
			"order_total_amount": doc.order_total_amount or 0,
			"received_amount": doc.received_amount or 0,
			"refunded_amount": doc.refunded_amount or 0,
			"pending_receipt_amount": doc.pending_receipt_amount or 0,
			"estimated_cost_amount": doc.estimated_cost_amount or 0,
			"actual_cost_amount": doc.actual_cost_amount or 0,
			"paid_amount": doc.paid_amount or 0,
			"pending_payment_amount": doc.pending_payment_amount or 0,
			"estimated_profit_amount": doc.estimated_profit_amount or 0,
			"actual_profit_amount": doc.actual_profit_amount or 0,
			"currency": doc.currency,
		},
		"cost_items": frappe.get_all(
			"Tour Cost Item",
			filters={"tour_order": tour_order, "docstatus": ["<", 2]},
			fields=[
				"name",
				"cost_category",
				"cost_name",
				"supplier",
				"estimated_amount",
				"actual_amount",
				"cost_date",
				"status",
				"docstatus",
			],
			order_by="cost_date desc, modified desc",
			limit_page_length=20,
		),
		"payment_ledgers": frappe.get_all(
			"Tour Payment Ledger",
			filters={"tour_order": tour_order, "docstatus": ["<", 2]},
			fields=[
				"name",
				"transaction_type",
				"payment_category",
				"amount",
				"transaction_date",
				"payment_method",
				"finance_confirmed",
				"docstatus",
			],
			order_by="transaction_date desc, modified desc",
			limit_page_length=20,
		),
		"supplier_payments": frappe.get_all(
			"Supplier Payment Record",
			filters={"tour_order": tour_order, "docstatus": ["<", 2]},
			fields=[
				"name",
				"supplier",
				"transaction_type",
				"payment_category",
				"amount",
				"payment_date",
				"payment_method",
				"finance_confirmed",
				"docstatus",
			],
			order_by="payment_date desc, modified desc",
			limit_page_length=20,
		),
	}


@frappe.whitelist()
def add_cost_item_from_overview(
	tour_order,
	cost_category,
	cost_name,
	estimated_amount=0,
	actual_amount=0,
	supplier=None,
	cost_date=None,
):
	tour_order_doc = get_tour_order_for_write(tour_order)
	doc = frappe.get_doc(
		{
			"doctype": "Tour Cost Item",
			"tour_order": tour_order_doc.name,
			"customer": tour_order_doc.customer,
			"supplier": supplier,
			"cost_category": cost_category,
			"cost_name": cost_name,
			"quantity": 1,
			"estimated_amount": flt(estimated_amount),
			"actual_amount": flt(actual_amount),
			"cost_date": cost_date or nowdate(),
			"status": "已确认",
			"finance_confirmed": 1,
		}
	)
	doc.insert()
	doc.submit()
	return {"name": doc.name, "overview": get_tour_order_overview(tour_order_doc.name)}


@frappe.whitelist()
def add_payment_ledger_from_overview(
	tour_order,
	transaction_type,
	payment_category,
	amount,
	transaction_date=None,
	payment_method=None,
):
	tour_order_doc = get_tour_order_for_write(tour_order)
	doc = frappe.get_doc(
		{
			"doctype": "Tour Payment Ledger",
			"tour_order": tour_order_doc.name,
			"customer": tour_order_doc.customer,
			"transaction_type": transaction_type,
			"payment_category": payment_category,
			"amount": flt(amount),
			"transaction_date": transaction_date or nowdate(),
			"payment_method": payment_method or "微信",
			"operator": frappe.session.user,
			"finance_confirmed": 1,
		}
	)
	doc.insert()
	doc.submit()
	return {"name": doc.name, "overview": get_tour_order_overview(tour_order_doc.name)}


@frappe.whitelist()
def add_supplier_payment_from_overview(
	tour_order,
	supplier,
	transaction_type,
	payment_category,
	amount,
	payment_date=None,
	payment_method=None,
):
	tour_order_doc = get_tour_order_for_write(tour_order)
	doc = frappe.get_doc(
		{
			"doctype": "Supplier Payment Record",
			"tour_order": tour_order_doc.name,
			"customer": tour_order_doc.customer,
			"supplier": supplier,
			"transaction_type": transaction_type,
			"payment_category": payment_category,
			"amount": flt(amount),
			"payment_date": payment_date or nowdate(),
			"payment_method": payment_method or "对公转账",
			"operator": frappe.session.user,
			"finance_confirmed": 1,
		}
	)
	doc.insert()
	doc.submit()
	return {"name": doc.name, "overview": get_tour_order_overview(tour_order_doc.name)}


def get_tour_order_for_write(tour_order):
	doc = frappe.get_doc("Tour Order", tour_order)
	doc.check_permission("write")
	return doc
