$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"
Set-Location "D:\github\DRL Agents\DQN web vul"
$py = ".\.venv312\Scripts\python.exe"
$logDir = "logs\live_scans\all_seeds_$(Get-Date -Format yyyyMMdd_HHmmss)"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$targets = @{
    "ecommerce" = "http://localhost:5002"
    "social"    = "http://localhost:5003"
    "banking"   = "http://localhost:5004"
    "blog"      = "http://localhost:5005"
    "fileshare" = "http://localhost:5006"
}

$seeds = 1,2,3,4,5

foreach ($seed in $seeds) {
    $model = "checkpoints/ablation/d3qn_full_seed${seed}_ep3000.pth"
    foreach ($key in $targets.Keys) {
        $url = $targets[$key]
        $logFile = "$logDir\${key}_seed${seed}.log"
        Write-Output "=== seed$seed / $key ($url) ==="
        & $py autonomous_scan.py $url --depth 150 --intensity 100 --model $model *> $logFile
    }
}

New-Item -ItemType File -Force -Path "$logDir\ALL_DONE.marker" | Out-Null
Write-Output "ALL 25 SCANS COMPLETE: $logDir"
