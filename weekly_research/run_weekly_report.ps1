# Weekly Research Report Generator
# PowerShell Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Weekly Research Report Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Generating weekly research report..." -ForegroundColor Yellow
Write-Host ""

# Run the Python script
python weekly_research_generator.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Report Generation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Reports are saved in the weekly_research folder" -ForegroundColor White
Write-Host ""

# List the reports in the folder
if (Test-Path "weekly_research") {
    Write-Host "Available reports:" -ForegroundColor Yellow
    Get-ChildItem "weekly_research" -Filter "*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor White
    }
}

Write-Host ""
Read-Host "Press Enter to continue" 