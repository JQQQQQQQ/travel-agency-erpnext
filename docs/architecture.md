# 架构方案

## 目标

系统需要满足以下要求：

- 先在本地可运行
- 后续可以部署到云服务器
- 数据可备份、可迁移
- 服务器不可用时，可迁回本地继续使用
- 所有业务定制独立于 ERPNext 官方源码

## 总体结构

```text
用户
  |
  v
ERPNext Web
  |
  +-- 标准 ERPNext 能力
  |
  +-- travel_agency 自定义 app
          |
          +-- Tour Order
          +-- Tour Payment Ledger
          +-- Tour Cost Item
          +-- Supplier Payment Record
          +-- 报表与自动汇总
  |
  v
MariaDB / Redis / Sites 附件目录
```

## 代码组织原则

### 1. 不修改 ERPNext 官方源码

所有旅行社业务逻辑都放在独立 app：

- `src/travel_agency/`

### 2. 部署、数据、代码分离

- 部署配置：`deploy/`
- 业务文档：`docs/`
- 运维脚本：`scripts/`
- 自定义代码：`src/travel_agency/`

### 3. 本地与服务器尽量同构

后续本地与服务器统一使用容器方案，减少环境差异。

## 当前本地环境结论

已确认：

- GitHub 账号已登录：`JQQQQQQQ`
- 当前 WSL 中未接入 Docker Desktop
- Windows Docker CLI 存在，但 Docker Linux Engine 当前未运行

因此本地下一步前置条件是启动 Docker Desktop。

## 业务一期范围

### 主业务单据

1. `Tour Order`
2. `Tour Payment Ledger`
3. `Tour Cost Item`
4. `Supplier Payment Record`

### 一期报表

1. 团款未收报表
2. 供应商待付报表
3. 团单利润报表
4. 月度经营汇总

## 部署策略

### 本地体验阶段

优先采用官方 `frappe_docker` 的 demo 方案验证 ERPNext 可运行，再逐步接入自定义 app。

### 服务器阶段

采用正式的 Compose 部署，并增加：

- 数据持久化
- 每日备份
- 恢复文档
- 版本化发布
