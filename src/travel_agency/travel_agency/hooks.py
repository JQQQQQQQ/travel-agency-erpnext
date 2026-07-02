app_name = "travel_agency"
app_title = "Travel Agency"
app_publisher = "JQQQQQQQ"
app_description = "Travel agency management customizations for ERPNext"
app_email = "admin@example.com"
app_license = "MIT"

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["module", "=", "Travel Agency"]],
	},
]

after_migrate = "travel_agency.setup.configure_chinese_defaults"
