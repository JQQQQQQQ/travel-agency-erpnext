# 旅行社管理系统

基于 ERPNext 的旅行社业务管理系统，面向小团队场景，优先解决以下问题：

- 团单管理
- 团款收款与退款
- 供应商成本与付款
- 团单利润与未收未付报表
- 自托管部署与数据可迁移

## 当前阶段

当前已经完成基础可用版本：

1. 本地 ERPNext demo 环境。
2. 旅行社业务自定义 app `travel_agency`。
3. 团单、收款、成本、付款核心闭环。
4. 团单利润表、应收应付汇总表。
5. 旅行社管理工作台。
6. 团单列表快捷筛选。
7. CSV 数据导入模板。

## 计划目录

```text
.
├── deploy/              # 部署配置与环境变量模板
├── docs/                # 架构、运维、恢复文档
├── templates/           # 数据导入模板
├── scripts/             # 本地检查、备份恢复辅助脚本
└── src/
    └── travel_agency/   # 旅行社业务自定义 app 代码
```

## 本地启动前提

本地优先采用 Docker Desktop + WSL2 方式运行。

当前本地 demo 默认访问地址：

- `http://localhost:8080`

本机 WSL 环境中可能没有可用的 `docker` 命令，当前脚本优先通过 Windows 侧 Docker CLI 执行。

## 本地检查

Windows PowerShell 中运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local-env.ps1
```

## 后续开发路线

第一期已完成：

1. `Tour Order` 旅行团单
2. `Tour Payment Ledger` 团款流水
3. `Tour Cost Item` 团单费用明细
4. `Supplier Payment Record` 业务付款单
5. 自动汇总与核心报表
6. 旅行社管理工作台
7. 团单列表快捷筛选
8. CSV 数据导入模板

## 数据导入

CSV 模板位于：

```text
templates/data_import/
```

导入说明见：

```text
docs/data-import.md
```

推荐导入顺序：

1. 客户
2. 供应商
3. 旅行团单
4. 团款流水
5. 团单费用明细
6. 供应商付款单

## 官方部署参考

本项目本地体验阶段优先参考 Frappe 官方 `frappe_docker`：

- 官方仓库：<https://github.com/frappe/frappe_docker>

根据该仓库 README，官方提供：

- `pwd.yml`：本地快速体验用的单文件 demo
- `compose.yaml`：生产部署基础文件

后续本仓库会在此基础上加上旅行社自定义 app 和业务配置。
