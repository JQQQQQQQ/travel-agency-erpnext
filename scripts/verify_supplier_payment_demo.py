import frappe


def make_customer():
	customer_name = "测试客户-供应商付款Demo"
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


def make_supplier():
	supplier_name = "测试供应商-付款Demo"
	if not frappe.db.exists("Supplier", supplier_name):
		supplier_group = frappe.db.get_value("Supplier Group", {}, "name")
		supplier = frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": supplier_name,
				"supplier_group": supplier_group,
				"supplier_type": "Company",
			}
		)
		supplier.insert(ignore_permissions=True)
	return supplier_name


def make_tour_order(customer):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Order",
			"tour_order_name": "供应商付款测试团",
			"tour_type": "定制团",
			"customer": customer,
			"sales_owner": "Administrator",
			"order_status": "待确认",
			"departure_date": "2026-08-28",
			"destination": "四川",
			"traveler_count": 5,
			"currency": "CNY",
			"order_total_amount": 15000,
			"received_amount": 10000,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def submit_cost(tour_order, supplier, actual_amount):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Cost Item",
			"tour_order": tour_order.name,
			"customer": tour_order.customer,
			"supplier": supplier,
			"cost_category": "地接",
			"cost_name": "四川地接服务",
			"quantity": 1,
			"estimated_amount": actual_amount,
			"actual_amount": actual_amount,
			"cost_date": "2026-07-02",
			"status": "已确认",
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


def submit_supplier_payment(tour_order, supplier, transaction_type, category, amount, cost_item=None):
	doc = frappe.get_doc(
		{
			"doctype": "Supplier Payment Record",
			"tour_order": tour_order.name,
			"customer": tour_order.customer,
			"supplier": supplier,
			"cost_item": cost_item,
			"transaction_type": transaction_type,
			"payment_category": category,
			"amount": amount,
			"payment_date": "2026-07-02",
			"payment_method": "对公转账",
			"operator": "Administrator",
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


def assert_amounts(tour_order_name, actual_cost, paid, pending_payment, actual_profit):
	doc = frappe.get_doc("Tour Order", tour_order_name)
	assert doc.actual_cost_amount == actual_cost, (doc.actual_cost_amount, actual_cost)
	assert doc.paid_amount == paid, (doc.paid_amount, paid)
	assert doc.pending_payment_amount == pending_payment, (doc.pending_payment_amount, pending_payment)
	assert doc.actual_profit_amount == actual_profit, (doc.actual_profit_amount, actual_profit)
	return doc


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	customer = make_customer()
	supplier = make_supplier()
	tour_order = make_tour_order(customer)
	cost_item = submit_cost(tour_order, supplier, 6000)
	assert_amounts(tour_order.name, 6000, 0, 6000, 4000)

	advance = submit_supplier_payment(tour_order, supplier, "付款", "预付款", 2000, cost_item.name)
	assert_amounts(tour_order.name, 6000, 2000, 4000, 4000)

	balance = submit_supplier_payment(tour_order, supplier, "付款", "尾款", 3000, cost_item.name)
	assert_amounts(tour_order.name, 6000, 5000, 1000, 4000)

	refund = submit_supplier_payment(tour_order, supplier, "退款", "退款", 500, cost_item.name)
	assert_amounts(tour_order.name, 6000, 4500, 1500, 4000)
	frappe.db.commit()

	try:
		submit_supplier_payment(tour_order, supplier, "付款", "补款", 2000, cost_item.name)
	except Exception:
		frappe.db.rollback()
	else:
		raise AssertionError("超额付款应该被拦截")

	try:
		submit_supplier_payment(tour_order, supplier, "退款", "退款", 5000, cost_item.name)
	except Exception:
		frappe.db.rollback()
	else:
		raise AssertionError("超额退款应该被拦截")

	refund.cancel()
	assert_amounts(tour_order.name, 6000, 5000, 1000, 4000)

	print(f"Tour Order: {tour_order.name}")
	print(f"Cost Item: {cost_item.name}")
	print(f"Advance Payment: {advance.name}")
	print(f"Balance Payment: {balance.name}")
	print("Supplier payment verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
