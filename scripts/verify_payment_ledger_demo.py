import frappe


def make_customer():
	customer_name = "测试客户-团款流水Demo"
	if not frappe.db.exists("Customer", customer_name):
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_type": "Individual",
				"customer_group": "Individual",
				"territory": "All Territories",
			}
		)
		customer.insert(ignore_permissions=True)
	return customer_name


def make_tour_order(customer):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Order",
			"tour_order_name": "团款流水测试团",
			"tour_type": "定制团",
			"customer": customer,
			"sales_owner": "Administrator",
			"order_status": "待确认",
			"departure_date": "2026-08-08",
			"destination": "贵州",
			"traveler_count": 3,
			"currency": "CNY",
			"order_total_amount": 9000,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def submit_payment(tour_order, transaction_type, category, amount):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Payment Ledger",
			"tour_order": tour_order.name,
			"customer": tour_order.customer,
			"transaction_type": transaction_type,
			"payment_category": category,
			"amount": amount,
			"transaction_date": "2026-07-02",
			"payment_method": "微信",
			"operator": "Administrator",
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


def assert_amounts(tour_order_name, received, refunded, pending):
	doc = frappe.get_doc("Tour Order", tour_order_name)
	assert doc.received_amount == received, (doc.received_amount, received)
	assert doc.refunded_amount == refunded, (doc.refunded_amount, refunded)
	assert doc.pending_receipt_amount == pending, (doc.pending_receipt_amount, pending)
	return doc


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	customer = make_customer()
	tour_order = make_tour_order(customer)

	deposit = submit_payment(tour_order, "收款", "定金", 3000)
	assert_amounts(tour_order.name, 3000, 0, 6000)

	balance = submit_payment(tour_order, "收款", "尾款", 2000)
	assert_amounts(tour_order.name, 5000, 0, 4000)

	refund = submit_payment(tour_order, "退款", "退款", 1000)
	assert_amounts(tour_order.name, 5000, 1000, 5000)
	frappe.db.commit()

	try:
		submit_payment(tour_order, "退款", "退款", 6000)
	except Exception:
		frappe.db.rollback()
	else:
		raise AssertionError("超额退款应该被拦截")

	refund.cancel()
	assert_amounts(tour_order.name, 5000, 0, 4000)

	print(f"Tour Order: {tour_order.name}")
	print(f"Deposit: {deposit.name}")
	print(f"Balance: {balance.name}")
	print("Payment ledger verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
