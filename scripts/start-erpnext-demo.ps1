$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$RuntimeDir = Join-Path $RepoRoot "runtime"
$FrappeDockerDir = Join-Path $RuntimeDir "frappe_docker"

Write-Host "== 检查 Docker Engine ==" -ForegroundColor Cyan
docker version | Out-Host

Write-Host ""
Write-Host "== 准备 frappe_docker ==" -ForegroundColor Cyan
if (-not (Test-Path $RuntimeDir)) {
    New-Item -ItemType Directory -Path $RuntimeDir | Out-Null
}

if (-not (Test-Path $FrappeDockerDir)) {
    git clone https://github.com/frappe/frappe_docker $FrappeDockerDir
}

Write-Host ""
Write-Host "== 启动 ERPNext demo ==" -ForegroundColor Cyan
Push-Location $FrappeDockerDir
try {
    docker compose -f pwd.yml up -d
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "启动命令已执行。首次启动需要拉取镜像，耗时会比较久。" -ForegroundColor Green
Write-Host "启动后访问地址通常为：http://localhost:8080"
Write-Host "如果端口不同，请执行：docker compose -f runtime/frappe_docker/pwd.yml ps"
