# 旅行社数据导入说明

本文档说明如何使用 `templates/data_import` 目录下的 CSV 模板，把旧表格数据迁移到旅行社管理系统。

## 模板文件

- `customer_import.csv`：客户基础资料。
- `supplier_import.csv`：供应商基础资料。
- `tour_order_import.csv`：旅行团单。
- `tour_payment_ledger_import.csv`：客户收款/退款流水。
- `tour_cost_item_import.csv`：团单费用明细。
- `supplier_payment_record_import.csv`：供应商付款/退款记录。

## 推荐导入顺序

1. 先导入客户：`Customer`。
2. 再导入供应商：`Supplier`。
3. 再导入旅行团单：`Tour Order`。
4. 导入团单后，从 `Tour Order` 列表导出系统生成的团单编号，例如 `TOUR-2026-00001`。
5. 把系统团单编号填到后续模板的 `tour_order` 列。
6. 再导入客户收款/退款流水：`Tour Payment Ledger`。
7. 再导入团单费用明细：`Tour Cost Item`。
8. 最后导入供应商付款/退款记录：`Supplier Payment Record`。

必须按这个顺序导入。后面的流水和费用都依赖前面的客户、供应商、团单，否则 Link 字段找不到数据会导入失败。

## 字段填写规则

日期字段统一使用 `YYYY-MM-DD` 格式，例如 `2026-08-08`。

金额字段只填写数字，不要写货币符号，例如填写 `9000`，不要写 `¥9000`。

勾选字段使用 `1` 或 `0`：

- `1` 表示是，例如财务已确认。
- `0` 表示否。

不要导入这些系统自动计算字段：

- `pending_receipt_amount`：待收金额。
- `pending_payment_amount`：待付金额。
- `estimated_profit_amount`：预计毛利。
- `actual_profit_amount`：实际毛利。

这些字段由系统根据收款、退款、成本、付款自动计算。

## 可选值说明

`Tour Order.tour_type` 只能填写：

- `散拼`
- `私团`
- `定制团`
- `企业团`

`Tour Order.order_status` 只能填写：

- `待确认`
- `已确认`
- `已收定金`
- `收款中`
- `已收清`
- `已出团`
- `已完团`
- `已取消`
- `已退款完成`

`Tour Payment Ledger.transaction_type` 只能填写：

- `收款`
- `退款`

`Tour Payment Ledger.payment_category` 只能填写：

- `定金`
- `尾款`
- `补款`
- `退款`
- `其他`

`Tour Cost Item.cost_category` 只能填写：

- `酒店`
- `车队`
- `门票`
- `导游`
- `餐费`
- `机票`
- `火车票`
- `签证`
- `保险`
- `地接`
- `其他`

`Tour Cost Item.status` 只能填写：

- `待确认`
- `已确认`
- `有争议`
- `已取消`

`Supplier Payment Record.transaction_type` 只能填写：

- `付款`
- `退款`

`Supplier Payment Record.payment_category` 只能填写：

- `预付款`
- `尾款`
- `补款`
- `退款`
- `其他`

付款方式字段只能填写：

- `微信`
- `支付宝`
- `现金`
- `银行卡`
- `对公转账`
- `其他`

## ERPNext 页面操作

1. 进入 ERPNext。
2. 搜索并打开 `Data Import`。
3. 点击新建。
4. 选择要导入的 DocType，例如 `Tour Order`。
5. 选择导入类型：
   - 新增数据选 `Insert New Records`。
   - 更新已有数据选 `Update Existing Records`。
6. 上传对应 CSV 文件。
7. 点击预览，确认没有字段错误。
8. 点击开始导入。

## 常见错误

如果提示客户不存在，先导入 `Customer`，或者确认 `customer` 列填写的是系统中的客户名称。

如果提示供应商不存在，先导入 `Supplier`，或者确认 `supplier` 列填写的是系统中的供应商名称。

如果提示团单不存在，先导入 `Tour Order`，然后从系统导出团单编号，再填写到后续模板的 `tour_order` 列。

如果提示选项无效，检查字段是否严格使用本文档中的可选值。不要添加空格或使用近似词。

如果提示金额校验失败，检查金额是否为正数。收款、退款、供应商付款、供应商退款金额都必须大于 0。

## 正式迁移建议

正式迁移前，先用 3 到 5 条旧数据做测试导入。确认团单列表、团单利润表、应收应付汇总表金额正确后，再导入完整历史数据。

完整历史数据建议按月份分批导入，方便定位错误和回滚。
