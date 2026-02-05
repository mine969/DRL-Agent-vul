$apps = @(
    "env/target_app_ecommerce.py",
    "env/target_app_social.py",
    "env/target_app_banking.py",
    "env/target_app_blog.py",
    "env/target_app_fileshare.py"
)

foreach ($app in $apps) {
    Write-Host "Starting $app..."
    Start-Process python -ArgumentList $app -WindowStyle Hidden
}

Write-Host "All targets started! Waiting 5s for initialization..."
Start-Sleep -Seconds 5
Get-NetTCPConnection -LocalPort 5002,5003,5004,5005,5006 -ErrorAction SilentlyContinue | Select-Object LocalPort, State
