# ============================================================================
# Monitor Multi-Target Training - PowerShell Version
# ============================================================================

Write-Host "Starting training from Episode 300 with NEW OSINT actions..." -ForegroundColor Cyan
Write-Host ""
Write-Host "New features:" -ForegroundColor Yellow
Write-Host "  - 5 OSINT actions (was 2)"
Write-Host "  - 100+ sensitive files to scan (was 10)"
Write-Host "  - Directory listing detection"
Write-Host "  - API discovery"
Write-Host "  - Subdomain enumeration"
Write-Host ""
Write-Host "Press any key to start training in a new window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open new PowerShell window and run training
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\github\RL; .\.venv\Scripts\Activate.ps1; python train_multi_target.py --episodes 1000 --resume 300"

Write-Host ""
Write-Host "✅ Training started in new window!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now:" -ForegroundColor Cyan
Write-Host "- Watch the live training progress"
Write-Host "- Press Ctrl+C in that window to stop and save checkpoint"
Write-Host "- Close this window"
Write-Host ""
Read-Host "Press Enter to close this window"
