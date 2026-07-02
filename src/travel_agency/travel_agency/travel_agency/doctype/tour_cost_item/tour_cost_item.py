import frappe
from frappe.model.document import Document


class TourCostItem(Document):
	def validate(self):
		self.set_customer_from_tour_order()
		self.set_missing_amounts()
		self.validate_amounts()

	def on_submit(self):
		self.update_tour_order_totals()

	def on_cancel(self):
		self.update_tour_order_totals()

	def set_customer_from_tour_order(self):
		if self.tour_order and not self.customer:
			self.customer = frappe.db.get_value("Tour Order", self.tour_order, "customer")

	def set_missing_amounts(self):
		if self.estimated_amount is None:
			self.estimated_amount = 0
		if self.actual_amount is None:
			self.actual_amount = 0

	def validate_amounts(self):
		if self.estimated_amount < 0 or self.actual_amount < 0:
			frappe.throw("预计金额和实际金额不能为负数")

		if self.estimated_amount == 0 and self.actual_amount == 0:
			frappe.throw("预计金额和实际金额至少填写一个")

	def update_tour_order_totals(self):
		if not self.tour_order:
			return

		tour_order = frappe.get_doc("Tour Order", self.tour_order)
		tour_order.recompute_cost_totals()
