import frappe

from travel_agency.travel_agency.report.receivable_payable_summary.receivable_payable_summary import (
	execute as execute_receivable_payable_summary,
)
from travel_agency.travel_agency.report.tour_order_profit_report.tour_order_profit_report import (
	execute as execute_tour_order_profit_report,
)


def make_customer():
	customer_name = "测试客户-报表Demo"
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
			"tour_order_name": "报表测试团",
			"tour_type": "定制团",
			"customer": customer,
			"sales_owner": "Administrator",
			"order_status": "收款中",
			"departure_date": "2026-09-08",
			"return_date": "2026-09-12",
			"destination": "重庆",
			"traveler_count": 6,
			"currency": "CNY",
			"order_total_amount": 18000,
			"received_amount": 10000,
			"estimated_cost_amount": 9000,
			"actual_cost_amount": 8000,
			"paid_amount": 3000,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	customer = make_customer()
	tour_order = make_tour_order(customer)
	filters = {
		"from_date": "2026-09-01",
		"to_date": "2026-09-30",
		"customer": customer,
	}

	profit_columns, profit_data, _, profit_chart = execute_tour_order_profit_report(filters)
	assert profit_columns
	assert profit_data
	assert profit_chart["type"] == "bar"
	profit_row = next(row for row in profit_data if row.tour_order == tour_order.name)
	assert profit_row.pending_receipt_amount == 8000, profit_row.pending_receipt_amount
	assert profit_row.pending_payment_amount == 5000, profit_row.pending_payment_amount
	assert profit_row.actual_profit_amount == 2000, profit_row.actual_profit_amount

	summary_columns, summary_data, _, summary_chart, report_summary = execute_receivable_payable_summary(
		{**filters, "only_pending": 1}
	)
	assert summary_columns
	assert summary_data
	assert summary_chart["type"] == "donut"
	assert report_summary
	summary_row = next(row for row in summary_data if row.tour_order == tour_order.name)
	assert summary_row.risk_status == "待收待付", summary_row.risk_status
	assert summary_row.cash_gap_amount == 3000, summary_row.cash_gap_amount

	report_names = {
		row.name
		for row in frappe.get_all(
			"Report",
			filters={"module": "Travel Agency"},
			fields=["name"],
		)
	}
	assert "Tour Order Profit Report" in report_names
	assert "Receivable Payable Summary" in report_names

	print(f"Tour Order: {tour_order.name}")
	print(f"Profit Report Rows: {len(profit_data)}")
	print(f"Receivable Payable Rows: {len(summary_data)}")
	print("Report verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
