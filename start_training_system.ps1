# Start Training System Script
# Launches all target environments and the training agent

Write-Host "🚀 Starting Web Security Training System..." -ForegroundColor Cyan

# 1. Start Target 1: Core App (Port 5001)
Write-Host "   Starting Target 1 (Core App)..." -NoNewline
Start-Process python -ArgumentList "env/target_app.py" -WorkingDirectory "d:\github\RL" -WindowStyle Minimized
Write-Host " Done." -ForegroundColor Green

# 2. Start Target 2: E-Commerce App (Port 5002)
Write-Host "   Starting Target 2 (E-Commerce)..." -NoNewline
Start-Process python -ArgumentList "env/target_app_ecommerce.py" -WorkingDirectory "d:\github\RL" -WindowStyle Minimized
Write-Host " Done." -ForegroundColor Green

# 3. Start Target 3: Social Media App (Port 5003)
Write-Host "   Starting Target 3 (Social Media)..." -NoNewline
Start-Process python -ArgumentList "env/target_app_social.py" -WorkingDirectory "d:\github\RL" -WindowStyle Minimized
Write-Host " Done." -ForegroundColor Green

# Wait for servers to initialize
Write-Host "⏳ Waiting 5 seconds for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 4. Start Training Agent
Write-Host "🤖 Starting Training Agent (2000 Episodes)..." -ForegroundColor Magenta
# We run this in the current window so the user can see the output
python -u train_multi_target.py --episodes 2000 --model checkpoints/multi_target_8k_ep0.pth --verbose
