@echo off
echo Syncing Repository...
git pull
git add -A
git commit -m "Auto-sync: %date% %time%"
git push
echo.
echo Sync Complete!
pause
