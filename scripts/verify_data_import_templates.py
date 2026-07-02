import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "data_import"


EXPECTED_HEADERS = {
	"customer_import.csv": [
		"customer_name",
		"customer_type",
		"customer_group",
		"territory",
	],
	"supplier_import.csv": [
		"supplier_name",
		"supplier_type",
		"supplier_group",
	],
	"tour_order_import.csv": [
		"tour_order_name",
		"tour_type",
		"customer",
		"contact",
		"sales_owner",
		"order_status",
		"departure_date",
		"return_date",
		"departure_city",
		"destination",
		"route_name",
		"traveler_count",
		"adult_count",
		"child_count",
		"currency",
		"order_total_amount",
		"internal_notes",
	],
	"tour_payment_ledger_import.csv": [
		"tour_order",
		"customer",
		"transaction_type",
		"payment_category",
		"amount",
		"transaction_date",
		"payment_method",
		"operator",
		"finance_confirmed",
		"remarks",
	],
	"tour_cost_item_import.csv": [
		"tour_order",
		"customer",
		"supplier",
		"cost_category",
		"cost_name",
		"quantity",
		"estimated_amount",
		"actual_amount",
		"cost_date",
		"status",
		"finance_confirmed",
		"remarks",
	],
	"supplier_payment_record_import.csv": [
		"tour_order",
		"customer",
		"supplier",
		"cost_item",
		"transaction_type",
		"payment_category",
		"amount",
		"payment_date",
		"payment_method",
		"operator",
		"finance_confirmed",
		"remarks",
	],
}


def read_csv(path):
	with path.open(newline="", encoding="utf-8") as file:
		return list(csv.reader(file))


def main():
	for filename, expected_headers in EXPECTED_HEADERS.items():
		path = TEMPLATE_DIR / filename
		assert path.exists(), path

		rows = read_csv(path)
		assert len(rows) >= 2, f"{filename} should include a header and at least one sample row"
		assert rows[0] == expected_headers, (filename, rows[0], expected_headers)

		width = len(rows[0])
		for index, row in enumerate(rows[1:], start=2):
			assert len(row) == width, f"{filename} row {index} has {len(row)} columns, expected {width}"

	print(f"Verified {len(EXPECTED_HEADERS)} data import templates")


if __name__ == "__main__":
	main()
