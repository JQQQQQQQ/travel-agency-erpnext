# 旅行社管理系统

基于 ERPNext 的旅行社业务管理系统，面向小团队场景，优先解决以下问题：

- 团单管理
- 团款收款与退款
- 供应商成本与付款
- 团单利润与未收未付报表
- 自托管部署与数据可迁移

## 当前阶段

当前仓库处于初始化阶段，先完成两部分：

1. 本地和服务器统一的部署底盘
2. 旅行社业务自定义 app `travel_agency`

## 计划目录

```text
.
├── deploy/              # 部署配置与环境变量模板
├── docs/                # 架构、运维、恢复文档
├── scripts/             # 本地检查、备份恢复辅助脚本
└── src/
    └── travel_agency/   # 后续自定义 app 代码
```

## 本地启动前提

本地优先采用 Docker Desktop + WSL2 方式运行。

当前已确认：

- GitHub 已登录
- 本机 WSL 环境中暂时没有可用的 `docker` 命令
- Windows 侧 Docker CLI 已存在，但 Docker Linux Engine 未启动

因此下一步需要先启动 Docker Desktop，再继续本地 ERPNext 容器启动。

## 本地检查

Windows PowerShell 中运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local-env.ps1
```

## 后续开发路线

第一期范围：

1. `Tour Order` 旅行团单
2. `Tour Payment Ledger` 团款流水
3. `Tour Cost Item` 团单费用明细
4. `Supplier Payment Record` 业务付款单
5. 自动汇总与核心报表

## 官方部署参考

本项目本地体验阶段优先参考 Frappe 官方 `frappe_docker`：

- 官方仓库：<https://github.com/frappe/frappe_docker>

根据该仓库 README，官方提供：

- `pwd.yml`：本地快速体验用的单文件 demo
- `compose.yaml`：生产部署基础文件

后续本仓库会在此基础上加上旅行社自定义 app 和业务配置。
