#!/usr/bin/env pwsh
# Setup and Test Script for Generative-Art
# This script automates the setup process and tests SVG generation

Write-Host "=== Generative-Art Setup and Test ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Step 2: Create virtual environment
Write-Host ""
Write-Host "[2/5] Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ℹ Virtual environment already exists, skipping creation..." -ForegroundColor Cyan
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Virtual environment created successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Activate virtual environment and install dependencies
Write-Host ""
Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  Upgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel 2>&1 | Out-Null

Write-Host "  Installing packages (this may take a few minutes)..." -ForegroundColor Cyan
# Install binary packages first (numpy, pycairo need prebuilt wheels on Windows)
& ".\venv\Scripts\pip.exe" install numpy pycairo --only-binary :all: 2>&1 | Out-Null
# Install other pure Python packages
& ".\venv\Scripts\pip.exe" install docopt tweepy perlin-noise 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ All dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Some dependencies may have failed to install" -ForegroundColor Yellow
}

# Step 4: Create .test directory
Write-Host ""
Write-Host "[4/5] Creating .test directory..." -ForegroundColor Yellow
if (!(Test-Path ".test")) {
    New-Item -Path ".test" -ItemType Directory | Out-Null
    Write-Host "  ✓ .test directory created" -ForegroundColor Green
} else {
    Write-Host "  ℹ .test directory already exists" -ForegroundColor Cyan
}

# Step 5: Test generation with Line_Grid.py
Write-Host ""
Write-Host "[5/5] Testing SVG generation..." -ForegroundColor Yellow

# Test with multiple scripts
$testScripts = @("Line_Grid.py", "Vertical_Lines.py", "Circular.py", "Mosaic_Circles.py")
$successCount = 0

foreach ($script in $testScripts) {
    if (Test-Path $script) {
        Write-Host "  Running $script..." -ForegroundColor Cyan
        & ".\venv\Scripts\python.exe" $script False True False 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            $successCount++
        }
    }
}

if ($successCount -eq $testScripts.Count) {
    Write-Host "  ✓ All test scripts executed successfully ($successCount/$($testScripts.Count))" -ForegroundColor Green
    Write-Host "  SVG files saved to Images/<script_name>/0-svg/" -ForegroundColor Cyan
} elseif ($successCount -gt 0) {
    Write-Host "  ⚠ Some tests passed ($successCount/$($testScripts.Count))" -ForegroundColor Yellow
} else {
    Write-Host "  ✗ Test generation failed" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment manually, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To generate artwork, run scripts directly:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\python.exe Line_Grid.py False True False" -ForegroundColor White
Write-Host "  (Arguments: open_file=False, svg=True, twitter=False)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Note: The 'generate' tool requires Linux. On Windows, run scripts directly." -ForegroundColor Yellow
Write-Host ""
