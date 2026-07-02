import frappe
from frappe.model.document import Document


class TourPaymentLedger(Document):
	def validate(self):
		self.set_customer_from_tour_order()
		self.validate_amount()
		self.validate_refund_amount()

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

		received_amount = frappe.db.get_value("Tour Order", self.tour_order, "received_amount") or 0
		refunded_amount = frappe.db.get_value("Tour Order", self.tour_order, "refunded_amount") or 0
		current_refund = self.amount or 0

		if self.docstatus == 1:
			current_refund = 0

		if refunded_amount + current_refund > received_amount:
			frappe.throw("退款金额不能超过该团单累计已收未退金额")

	def update_tour_order_totals(self):
		if not self.tour_order:
			return

		tour_order = frappe.get_doc("Tour Order", self.tour_order)
		tour_order.recompute_payment_totals()
