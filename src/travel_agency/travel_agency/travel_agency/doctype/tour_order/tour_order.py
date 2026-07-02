import frappe
from frappe.model.document import Document


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
