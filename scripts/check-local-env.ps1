$ErrorActionPreference = "Stop"

Write-Host "== GitHub 登录状态 ==" -ForegroundColor Cyan
gh auth status

Write-Host ""
Write-Host "== Docker CLI 检查 ==" -ForegroundColor Cyan
try {
    docker version --format "{{.Server.Version}}"
} catch {
    Write-Host "Docker Engine 当前不可用，请先启动 Docker Desktop。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== Docker Compose 检查 ==" -ForegroundColor Cyan
try {
    docker compose version
} catch {
    Write-Host "Docker Compose 当前不可用，请检查 Docker Desktop 和 WSL 集成。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== 建议下一步 ==" -ForegroundColor Cyan
Write-Host "1. 启动 Docker Desktop"
Write-Host "2. 打开 WSL Integration"
Write-Host "3. 在 WSL 中执行 docker version"
Write-Host "4. 通过后再开始 ERPNext 本地容器启动"
