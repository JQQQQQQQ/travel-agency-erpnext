import frappe
from frappe.model.document import Document


class SupplierPaymentRecord(Document):
	def validate(self):
		self.set_customer_from_tour_order()
		self.validate_amount()
		self.validate_refund_amount()
		self.validate_over_payment()

	def on_submit(self):
		self.update_tour_order_totals()

	def on_cancel(self):
		self.update_tour_order_totals()

	def set_customer_from_tour_order(self):
		if self.tour_order and not self.customer:
			self.customer = frappe.db.get_value("Tour Order", self.tour_order, "customer")

	def validate_amount(self):
		if (self.amount or 0) <= 0:
			frappe.throw("金额必须大于 0")

	def validate_refund_amount(self):
		if self.transaction_type != "退款" or not self.tour_order:
			return

		paid_amount = frappe.db.get_value("Tour Order", self.tour_order, "paid_amount") or 0
		current_refund = self.amount or 0

		if self.docstatus == 1:
			current_refund = 0

		if current_refund > paid_amount:
			frappe.throw("供应商退款金额不能超过该团单累计已付金额")

	def validate_over_payment(self):
		if self.transaction_type != "付款" or not self.tour_order:
			return

		actual_cost = frappe.db.get_value("Tour Order", self.tour_order, "actual_cost_amount") or 0
		if actual_cost <= 0:
			return

		paid_amount = frappe.db.get_value("Tour Order", self.tour_order, "paid_amount") or 0
		current_payment = self.amount or 0

		if self.docstatus == 1:
			current_payment = 0

		if paid_amount + current_payment > actual_cost:
			frappe.throw("供应商付款金额不能超过该团单实际成本")

	def update_tour_order_totals(self):
		if not self.tour_order:
			return

		tour_order = frappe.get_doc("Tour Order", self.tour_order)
		tour_order.recompute_supplier_payment_totals()
