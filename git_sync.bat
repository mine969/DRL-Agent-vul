@echo off
REM Auto-sync script for DRL-Agent-vul (Windows)
REM Usage: git_sync.bat "your commit message"

echo 🔄 Starting Git sync...

REM 1. Add all changes
git add -A
echo ✅ Staged all changes

REM 2. Commit with message
if "%~1"=="" (
    REM No message provided, use default with timestamp
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
    git commit -m "chore: Auto-sync %mydate% %mytime%" 2>nul || echo ⚠️  No changes to commit
) else (
    git commit -m "%~1" 2>nul || echo ⚠️  No changes to commit
)

REM 3. Pull with rebase (handles diverged branches)
echo 📥 Pulling latest changes...
git pull --rebase origin master

REM 4. Push
echo 📤 Pushing to GitHub...
git push origin master

if %errorlevel% equ 0 (
    echo ✅ Sync complete!
) else (
    echo ❌ Push failed! Check errors above.
)
