$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$FrappeDockerDir = Join-Path $RepoRoot "runtime\frappe_docker"

if (-not (Test-Path $FrappeDockerDir)) {
    Write-Host "未找到 runtime\frappe_docker，无需停止。" -ForegroundColor Yellow
    exit 0
}

Push-Location $FrappeDockerDir
try {
    docker compose -f pwd.yml down
} finally {
    Pop-Location
}

Write-Host "ERPNext demo 已停止。" -ForegroundColor Green
