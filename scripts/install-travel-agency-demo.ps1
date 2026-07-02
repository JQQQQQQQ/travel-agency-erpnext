$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$AppPath = Join-Path $RepoRoot "src\travel_agency"
$SiteName = "frontend"
$Containers = @(
    "frappe_docker-backend-1",
    "frappe_docker-queue-long-1",
    "frappe_docker-queue-short-1",
    "frappe_docker-scheduler-1"
)

foreach ($Container in $Containers) {
    Write-Host "== Sync app to $Container ==" -ForegroundColor Cyan
    docker exec -u root $Container bash -lc "rm -rf /home/frappe/frappe-bench/apps/travel_agency"
    docker cp $AppPath "${Container}:/home/frappe/frappe-bench/apps/travel_agency"
    docker exec -u root $Container bash -lc "chown -R frappe:frappe /home/frappe/frappe-bench/apps/travel_agency"
    docker exec $Container bash -lc "cd /home/frappe/frappe-bench && ./env/bin/python -m pip install -e apps/travel_agency"
}

Write-Host "== Register app in apps.txt ==" -ForegroundColor Cyan
docker exec frappe_docker-backend-1 bash -lc "cd /home/frappe/frappe-bench && grep -qxF travel_agency sites/apps.txt || echo travel_agency >> sites/apps.txt"

Write-Host "== Install or migrate site ==" -ForegroundColor Cyan
$InstalledApps = docker exec frappe_docker-backend-1 bench --site $SiteName list-apps
if ($InstalledApps -match "travel_agency") {
    docker exec frappe_docker-backend-1 bash -lc "cd /home/frappe/frappe-bench && bench --site $SiteName migrate"
} else {
    docker exec frappe_docker-backend-1 bash -lc "cd /home/frappe/frappe-bench && bench --site $SiteName install-app travel_agency"
}

Write-Host "travel_agency demo app is ready." -ForegroundColor Green
