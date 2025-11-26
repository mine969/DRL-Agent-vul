# Auto-sync script for DRL-Agent-vul (PowerShell)
# Usage: .\git_sync.ps1 "your commit message"

param(
    [string]$CommitMessage = ""
)

Write-Host "🔄 Starting Git sync..." -ForegroundColor Cyan

# 1. Add all changes
git add -A
Write-Host "✅ Staged all changes" -ForegroundColor Green

# 2. Commit with message
if ($CommitMessage -eq "") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $CommitMessage = "chore: Auto-sync $timestamp"
}

try {
    git commit -m $CommitMessage 2>$null
} catch {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
}

# 3. Pull with rebase (handles diverged branches)
Write-Host "📥 Pulling latest changes..." -ForegroundColor Cyan
git pull --rebase origin master

# 4. Push
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
git push origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Sync complete!" -ForegroundColor Green
} else {
    Write-Host "❌ Push failed! Check errors above." -ForegroundColor Red
}
