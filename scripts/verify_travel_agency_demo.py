import frappe


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	doctype_name = frappe.db.get_value("DocType", "Tour Order", "name")
	print(f"DocType: {doctype_name}")

	customer_name = "测试客户-旅行社Demo"
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

	doc = frappe.get_doc(
		{
			"doctype": "Tour Order",
			"tour_order_name": "云南6日游-测试团",
			"tour_type": "定制团",
			"customer": customer_name,
			"sales_owner": "Administrator",
			"order_status": "待确认",
			"departure_date": "2026-08-01",
			"destination": "云南",
			"traveler_count": 4,
			"currency": "CNY",
			"order_total_amount": 12000,
			"received_amount": 5000,
			"refunded_amount": 0,
			"estimated_cost_amount": 8000,
			"actual_cost_amount": 7600,
			"paid_amount": 3000,
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	print(f"Tour Order: {doc.name}")
	print(f"Pending Receipt: {doc.pending_receipt_amount}")
	print(f"Pending Payment: {doc.pending_payment_amount}")
	print(f"Estimated Profit: {doc.estimated_profit_amount}")
	print(f"Actual Profit: {doc.actual_profit_amount}")

	frappe.destroy()


if __name__ == "__main__":
	main()
