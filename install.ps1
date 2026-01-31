# PSS Installer for Windows

$installDir = "$HOME\.pss"
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Force -Path $installDir
}

Write-Host "Installing PSS to $installDir..." -ForegroundColor Cyan

# Copy files
Copy-Item "pss.py" -Destination $installDir
Copy-Item "pss.bat" -Destination $installDir

# Add to User PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    Write-Host "Adding PSS to User PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", $currentPath + ";$installDir", "User")
    Write-Host "Installation complete! Please restart your terminal." -ForegroundColor Green
} else {
    Write-Host "PSS is already in your PATH." -ForegroundColor Green
    Write-Host "Installation complete!"
}

Write-Host "Try running: pss test.pss"
