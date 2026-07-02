from pathlib import Path

import frappe


EXPECTED_LIST_FIELDS = {
	"tour_order_name",
	"customer",
	"order_status",
	"departure_date",
	"destination",
	"traveler_count",
	"order_total_amount",
	"pending_receipt_amount",
	"actual_cost_amount",
	"pending_payment_amount",
	"actual_profit_amount",
}


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	doctype = frappe.get_doc("DocType", "Tour Order")
	assert doctype.sort_field == "departure_date", doctype.sort_field
	assert doctype.sort_order == "DESC", doctype.sort_order

	list_fields = {
		row.fieldname
		for row in doctype.fields
		if row.fieldname and row.fieldtype not in {"Section Break", "Column Break"} and row.in_list_view
	}
	assert EXPECTED_LIST_FIELDS.issubset(list_fields), list_fields
	assert "pending_payment_amount" in list_fields
	assert "sales_owner" not in list_fields
	assert "tour_type" not in list_fields

	list_js = Path(
		"/home/frappe/frappe-bench/apps/travel_agency/"
		"travel_agency/travel_agency/doctype/tour_order/tour_order_list.js"
	)
	content = list_js.read_text(encoding="utf-8")
	for text in ["待收款", "待付款", "即将出团", "清除筛选", "get_indicator"]:
		assert text in content, text

	print(f"Tour Order List Fields: {len(list_fields)}")
	print("Tour order list verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
