$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"
Set-Location "D:\github\DRL Agents\DQN web vul"
$py = ".\.venv312\Scripts\python.exe"
$model = "checkpoints/ablation/d3qn_full_seed5_ep3000.pth"
$stamp = Get-Date -Format yyyyMMdd_HHmmss
$logDir = "logs\live_scans\full_potential_$stamp"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$targets = @{
    "ecommerce" = "http://localhost:5002"
    "social"    = "http://localhost:5003"
    "banking"   = "http://localhost:5004"
    "blog"      = "http://localhost:5005"
    "fileshare" = "http://localhost:5006"
}

foreach ($key in $targets.Keys) {
    $url = $targets[$key]
    $logFile = "$logDir\$key.log"
    "=== $key ($url) starting $(Get-Date) ===" | Out-File $logFile
    & $py autonomous_scan.py $url --depth 150 --intensity 100 --model $model *>> $logFile
    "=== $key finished $(Get-Date) ===" | Out-File $logFile -Append
}

New-Item -ItemType File -Force -Path "$logDir\ALL_DONE.marker" | Out-Null
"ALL 5 SCANS COMPLETE" | Out-File "$logDir\ALL_DONE.marker"
