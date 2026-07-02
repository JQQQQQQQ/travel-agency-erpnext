import frappe

from travel_agency.travel_agency.doctype.tour_order.tour_order import (
	add_cost_item_from_overview,
	add_payment_ledger_from_overview,
	add_supplier_payment_from_overview,
	get_tour_order_overview,
)


def make_customer():
	customer_name = "测试客户-团单总览Demo"
	if not frappe.db.exists("Customer", customer_name):
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_type": "Individual",
				"customer_group": "Individual",
				"territory": "All Territories",
			}
		).insert(ignore_permissions=True)
	return customer_name


def make_supplier():
	supplier_name = "测试供应商-团单总览Demo"
	if not frappe.db.exists("Supplier", supplier_name):
		supplier_group = frappe.db.get_value("Supplier Group", {}, "name")
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": supplier_name,
				"supplier_group": supplier_group,
				"supplier_type": "Company",
			}
		).insert(ignore_permissions=True)
	return supplier_name


def make_tour_order(customer):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Order",
			"tour_order_name": "团单总览测试团",
			"tour_type": "定制团",
			"customer": customer,
			"sales_owner": "Administrator",
			"order_status": "收款中",
			"departure_date": "2026-10-01",
			"return_date": "2026-10-05",
			"destination": "桂林",
			"traveler_count": 4,
			"currency": "CNY",
			"order_total_amount": 16000,
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


def submit_cost(tour_order, supplier, amount):
	doc = frappe.get_doc(
		{
			"doctype": "Tour Cost Item",
			"tour_order": tour_order.name,
			"customer": tour_order.customer,
			"supplier": supplier,
			"cost_category": "地接",
			"cost_name": "桂林地接服务",
			"quantity": 1,
			"estimated_amount": amount,
			"actual_amount": amount,
			"cost_date": "2026-07-02",
			"status": "已确认",
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


def submit_supplier_payment(tour_order, supplier, amount):
	doc = frappe.get_doc(
		{
			"doctype": "Supplier Payment Record",
			"tour_order": tour_order.name,
			"customer": tour_order.customer,
			"supplier": supplier,
			"transaction_type": "付款",
			"payment_category": "预付款",
			"amount": amount,
			"payment_date": "2026-07-02",
			"payment_method": "对公转账",
			"operator": "Administrator",
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()
	frappe.set_user("Administrator")

	customer = make_customer()
	supplier = make_supplier()
	tour_order = make_tour_order(customer)
	payment = submit_payment(tour_order, "收款", "定金", 6000)
	cost = submit_cost(tour_order, supplier, 7000)
	supplier_payment = submit_supplier_payment(tour_order, supplier, 3000)

	overview = get_tour_order_overview(tour_order.name)
	assert overview["summary"]["order_total_amount"] == 16000
	assert overview["summary"]["received_amount"] == 6000
	assert overview["summary"]["actual_cost_amount"] == 7000
	assert overview["summary"]["paid_amount"] == 3000
	assert overview["summary"]["actual_profit_amount"] == -1000
	assert any(row.name == payment.name for row in overview["payment_ledgers"])
	assert any(row.name == cost.name for row in overview["cost_items"])
	assert any(row.name == supplier_payment.name for row in overview["supplier_payments"])

	inline_cost = add_cost_item_from_overview(
		tour_order.name,
		cost_category="酒店",
		cost_name="总览内新增酒店",
		supplier=supplier,
		estimated_amount=1200,
		actual_amount=1300,
		cost_date="2026-07-03",
	)
	inline_payment = add_payment_ledger_from_overview(
		tour_order.name,
		transaction_type="收款",
		payment_category="补款",
		amount=2000,
		transaction_date="2026-07-03",
		payment_method="银行卡",
	)
	inline_supplier_payment = add_supplier_payment_from_overview(
		tour_order.name,
		supplier=supplier,
		transaction_type="付款",
		payment_category="补款",
		amount=1000,
		payment_date="2026-07-03",
		payment_method="对公转账",
	)

	overview = get_tour_order_overview(tour_order.name)
	assert overview["summary"]["received_amount"] == 8000
	assert overview["summary"]["actual_cost_amount"] == 8300
	assert overview["summary"]["paid_amount"] == 4000
	assert overview["summary"]["actual_profit_amount"] == -300
	assert any(row.name == inline_cost["name"] for row in overview["cost_items"])
	assert any(row.name == inline_payment["name"] for row in overview["payment_ledgers"])
	assert any(row.name == inline_supplier_payment["name"] for row in overview["supplier_payments"])

	print(f"Tour Order: {tour_order.name}")
	print(f"Cost Items: {len(overview['cost_items'])}")
	print(f"Payment Ledgers: {len(overview['payment_ledgers'])}")
	print(f"Supplier Payments: {len(overview['supplier_payments'])}")
	print("Tour order overview verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
