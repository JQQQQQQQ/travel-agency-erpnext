# 本地部署说明

## 当前状态

本机当前问题不是 GitHub，也不是仓库，而是 Docker 引擎未启动。

检测结果：

- `gh auth status` 正常
- WSL 中 `docker` 不可用
- Windows 侧 Docker CLI 存在，但无法连接 `dockerDesktopLinuxEngine`

## 需要先完成的事

### 1. 启动 Docker Desktop

确认 Docker Desktop 已启动，并且启用了 WSL2 集成。

### 2. 在 WSL 中再次确认 Docker

```bash
docker version
docker compose version
```

如果仍然失败，检查 Docker Desktop 设置：

- Settings
- Resources
- WSL Integration
- 打开当前 WSL 发行版集成

## 官方本地体验方式

Frappe 官方 `frappe_docker` README 提供了本地快速体验用法：

```bash
git clone https://github.com/frappe/frappe_docker
cd frappe_docker
docker compose -f pwd.yml up -d
```

本仓库也提供了封装脚本。请在 Windows PowerShell 中进入项目目录后执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-erpnext-demo.ps1
```

停止 demo：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-erpnext-demo.ps1
```

说明：

- `pwd.yml` 适合短期体验
- 官方明确说明该方案是 disposable demo
- 该方案不适合作为最终正式定制环境

## 我们的建议

### 第一阶段

先用官方 demo 证明本机可以跑 ERPNext。

### 第二阶段

再把自定义业务 app `travel_agency` 接进去，进入功能开发。

## 启动完成后的验证

在 Docker Desktop 正常后，至少验证：

- Docker CLI 可用
- 容器能正常启动
- ERPNext 页面可打开
- 默认管理员可登录
