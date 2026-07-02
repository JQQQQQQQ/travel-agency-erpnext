import frappe
from frappe.translate import get_all_translations


EXPECTED_TRANSLATIONS = {
	"Tour Order": "旅行团单",
	"Tour Payment Ledger": "团款流水",
	"Tour Cost Item": "团单费用明细",
	"Supplier Payment Record": "供应商付款单",
	"Tour Order Profit Report": "团单利润表",
	"Receivable Payable Summary": "应收应付汇总表",
}


def main():
	frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()

	system_language = frappe.db.get_single_value("System Settings", "language")
	assert system_language in {"zh", "zh-CN"}, system_language

	administrator_language = frappe.db.get_value("User", "Administrator", "language")
	assert administrator_language in {"zh", "zh-CN"}, administrator_language

	translations = get_all_translations(system_language)
	for source, target in EXPECTED_TRANSLATIONS.items():
		assert translations.get(source) == target, (source, translations.get(source), target)

	workspace = frappe.get_doc("Workspace", "旅行社管理")
	assert workspace.label == "旅行社管理"

	print(f"System Language: {system_language}")
	print(f"Administrator Language: {administrator_language}")
	print("Chinese locale verification passed")

	frappe.destroy()


if __name__ == "__main__":
	main()
