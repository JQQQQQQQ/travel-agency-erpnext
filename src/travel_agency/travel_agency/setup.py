import frappe


def configure_chinese_defaults():
	language = get_available_chinese_language()
	if not language:
		return

	frappe.db.set_single_value("System Settings", "language", language)
	set_system_user_language(language)
	frappe.clear_cache()


def get_available_chinese_language():
	for language in ("zh", "zh-CN"):
		if frappe.db.exists("Language", language):
			return language
	return None


def set_system_user_language(language):
	users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User"},
		fields=["name", "language"],
	)

	for user in users:
		if not user.language or user.language in {"en", "zh", "zh-CN"}:
			frappe.db.set_value("User", user.name, "language", language, update_modified=False)
