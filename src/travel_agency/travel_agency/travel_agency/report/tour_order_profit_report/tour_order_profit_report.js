frappe.query_reports["Tour Order Profit Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: "出发日期从",
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: "出发日期到",
			fieldtype: "Date",
		},
		{
			fieldname: "customer",
			label: "客户",
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "order_status",
			label: "状态",
			fieldtype: "Select",
			options: "\n待确认\n已确认\n已收定金\n收款中\n已收清\n已出团\n已完团\n已取消\n已退款完成",
		},
	],
};
