import frappe


EXPECTED_LINKS = {
	"Tour Order": "DocType",
	"Tour Payment Ledger": "DocType",
	"Tour Cost Item": "DocType",
	"Supplier Payment Record": "DocType",
	"Tour Order Profit Report": "Report",
	"Receivable Payable Summary": "Report",
	"Customer": "DocType",
	"Supplier": "DocType",
}


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	workspace = frappe.get_doc("Workspace", "旅行社管理")
	assert workspace.public == 1
	assert workspace.module == "Travel Agency"
	assert workspace.icon == "map"

	links = {
		row.link_to: row.link_type
		for row in workspace.links
		if row.type == "Link" and row.link_to
	}

	for link_to, link_type in EXPECTED_LINKS.items():
		assert links.get(link_to) == link_type, (link_to, links.get(link_to), link_type)

	for doctype in [
		"Tour Order",
		"Tour Payment Ledger",
		"Tour Cost Item",
		"Supplier Payment Record",
	]:
		assert frappe.db.exists("DocType", doctype), doctype

	for report in ["Tour Order Profit Report", "Receivable Payable Summary"]:
		assert frappe.db.exists("Report", report), report

	print(f"Workspace: {workspace.name}")
	print(f"Workspace Links: {len(links)}")
	print("Workspace verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
