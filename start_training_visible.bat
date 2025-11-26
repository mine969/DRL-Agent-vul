@echo off
REM ============================================================================
REM Monitor Multi-Target Training - Opens in New Window
REM ============================================================================

echo Starting training from Episode 300 with NEW OSINT actions...
echo.
echo New features:
echo   - 5 OSINT actions (was 2)
echo   - 100+ sensitive files to scan (was 10)
echo   - Directory listing detection
echo   - API discovery
echo   - Subdomain enumeration
echo.
echo Press any key to start training in a new window...
pause >nul

REM Open new terminal and run training
start "DRL Agent Training - Multi-Target (Episode 300+)" cmd /k "cd /d d:\github\RL && .venv\Scripts\activate && python train_multi_target.py --episodes 1000 --resume 300"

echo.
echo ✅ Training started in new window!
echo.
echo You can now:
echo - Watch the live training progress
echo - Press Ctrl+C in that window to stop and save checkpoint
echo - Close this window
echo.
pause
