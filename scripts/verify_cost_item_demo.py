import frappe


def make_customer():
	customer_name = "测试客户-成本明细Demo"
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
			"tour_order_name": "成本明细测试团",
			"tour_type": "定制团",
			"customer": customer,
			"sales_owner": "Administrator",
			"order_status": "待确认",
			"departure_date": "2026-08-18",
			"destination": "云南",
			"traveler_count": 4,
			"currency": "CNY",
			"order_total_amount": 12000,
			"received_amount": 8000,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def submit_cost(tour_order, category, name, estimated_amount, actual_amount):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Cost Item",
			"tour_order": tour_order.name,
			"customer": tour_order.customer,
			"cost_category": category,
			"cost_name": name,
			"quantity": 1,
			"estimated_amount": estimated_amount,
			"actual_amount": actual_amount,
			"cost_date": "2026-07-02",
			"status": "已确认",
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


def assert_amounts(tour_order_name, estimated_cost, actual_cost, estimated_profit, actual_profit):
	doc = frappe.get_doc("Tour Order", tour_order_name)
	assert doc.estimated_cost_amount == estimated_cost, (doc.estimated_cost_amount, estimated_cost)
	assert doc.actual_cost_amount == actual_cost, (doc.actual_cost_amount, actual_cost)
	assert doc.estimated_profit_amount == estimated_profit, (doc.estimated_profit_amount, estimated_profit)
	assert doc.actual_profit_amount == actual_profit, (doc.actual_profit_amount, actual_profit)
	return doc


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	customer = make_customer()
	tour_order = make_tour_order(customer)

	hotel = submit_cost(tour_order, "酒店", "昆明酒店", 3000, 3200)
	assert_amounts(tour_order.name, 3000, 3200, 9000, 4800)

	bus = submit_cost(tour_order, "车队", "云南当地用车", 1800, 1600)
	assert_amounts(tour_order.name, 4800, 4800, 7200, 3200)
	frappe.db.commit()

	try:
		submit_cost(tour_order, "门票", "负数成本测试", -1, 0)
	except Exception:
		frappe.db.rollback()
	else:
		raise AssertionError("负数成本应该被拦截")

	bus.cancel()
	assert_amounts(tour_order.name, 3000, 3200, 9000, 4800)

	print(f"Tour Order: {tour_order.name}")
	print(f"Hotel Cost: {hotel.name}")
	print(f"Bus Cost: {bus.name}")
	print("Cost item verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
