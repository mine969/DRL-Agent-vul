# Real-World Hacking Simulation
# Target: All 5 Mock Applications
# Agent: Improved DQN Model (Episode 2400)
# Mode: Full Autonomous + Persistence

$python = ".venv\Scripts\python.exe"
$script = "autonomous_scan.py"
$model = "checkpoints/improved_mock_ep2400.pth"
$common_args = "--model $model --depth 10 --intensity 5 --persist --stealth low"

$targets = @(
    @{ Url = "http://localhost:5002"; Name = "E-Commerce" },
    @{ Url = "http://localhost:5003"; Name = "Social Media" },
    @{ Url = "http://localhost:5004"; Name = "Online Banking" },
    @{ Url = "http://localhost:5005"; Name = "Secure Blog" },
    @{ Url = "http://localhost:5006"; Name = "File Share" }
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🕵️  STARTING REAL-WORLD PENETRATION TEST SIMULATION" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Agent: $model" -ForegroundColor Gray
Write-Host "Mode: Autonomous | Intensity: 5 | Depth: 10 | Persist: ON" -ForegroundColor Gray
Write-Host ""

foreach ($t in $targets) {
    $name = $t.Name
    $url = $t.Url
    
    Write-Host "--------------------------------------------------------" -ForegroundColor Yellow
    Write-Host "🚀 TARGETING: $name ($url)" -ForegroundColor Yellow
    Write-Host "--------------------------------------------------------" -ForegroundColor Yellow
    
    # Execute the scan
    & $python $script $url $common_args.Split(' ')
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Scan Request Completed for $name" -ForegroundColor Green
    } else {
        Write-Host "❌ Scan Failed for $name" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🏁 ALL OPERATIONS COMPLETE" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
