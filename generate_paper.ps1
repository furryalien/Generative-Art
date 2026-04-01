#!/usr/bin/env pwsh
# Generate artwork with different paper sizes
# Usage: .\generate_paper.ps1 <script> <paper-size> [count] [line-width] [shape-type]

param(
    [Parameter(Mandatory=$true)]
    [string]$Script,
    
    [Parameter(Mandatory=$false)]
    [string]$PaperSize = "a6",
    
    [Parameter(Mandatory=$false)]
    [int]$Count = 1,
    
    [Parameter(Mandatory=$false)]
    [string]$LineWidth = "1.0",
    
    [Parameter(Mandatory=$false)]
    [string]$ShapeType = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$GearMode = $null,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Help text
if ($Help) {
    Write-Host @"
Generate artwork with specified paper sizes and line widths

Usage:
  .\generate_paper.ps1 <script> [paper-size] [count] [line-width] [shape-type]

Arguments:
  script      Name of the Python script to run (e.g., Line_Grid.py)
  paper-size  Paper size specification (default: a6)
  count       Number of images to generate (default: 1)
  line-width  Line width option (default: 1.0)
  shape-type  Shape type for Varied_Shapes.py (optional)

Paper Size Formats:
  a6                  A6 portrait at 300 DPI (1240x1748 px)
  a6-landscape        A6 landscape at 300 DPI (1748x1240 px)
  a6-200              A6 portrait at 200 DPI (827x1165 px)
  a6-landscape-200    A6 landscape at 200 DPI (1165x827 px)
  a5                  A5 portrait at 300 DPI
  a4                  A4 portrait at 300 DPI
  letter              US Letter at 300 DPI
  square-small        100mm square at 300 DPI

Available Paper Sizes:
  a6, a5, a4, a3, letter, legal
  square-small, square-medium, square-large

DPI Options:
  300 (high quality, default)
  200 (medium quality)
  150 (draft)

Line Width Options:
  <number>              Fixed width in pixels (e.g., 1.0, 2.5, 0.5)
  random-by-line        Each line gets its own random width
  random-all            All lines share one random width

Shape Type Options (for Varied_Shapes.py):
  circles, squares, triangles, stars, hearts, moons, clovers, diamonds, hexagons, pentagons
  lucky_charms          Mix of circles, stars, hearts, moons, clovers, diamonds
  geometric             Mix of circles, squares, triangles, hexagons, pentagons, diamonds
  all                   All 10 shape types

Gear Placement Options (for Meshed_Gears.py):
  clustered             Gears cluster together with tight meshing (default)
  random                Gears randomly placed with some meshing

Gear Size Options (for Meshed_Gears.py):
  Use -GearMode parameter with format: placement,size
  Examples:
    clustered,uniform   Clustered placement with all same-size gears (best meshing)
    clustered,varied    Clustered placement with different-size gears
    random,uniform      Random placement with same-size gears
    random,varied       Random placement with different-size gears

Examples:
  .\generate_paper.ps1 Line_Grid.py a6
  .\generate_paper.ps1 Circular.py a4-landscape 3
  .\generate_paper.ps1 Vertical_Lines.py a6-200 1 2.0
  .\generate_paper.ps1 Line_Grid.py a6-landscape 5 random-by-line
  .\generate_paper.ps1 Mosaic_Circles.py a6 3 random-all
  .\generate_paper.ps1 Varied_Shapes.py a6-landscape 5 random-by-line circles
  .\generate_paper.ps1 Varied_Shapes.py a6 3 1.5 all
  .\generate_paper.ps1 Meshed_Gears.py a6-landscape 5 random-by-line -GearMode clustered,uniform
  .\generate_paper.ps1 Meshed_Gears.py a6 3 1.5 -GearMode random,varied

"@ -ForegroundColor Cyan
    exit 0
}

# Check if script exists
if (!(Test-Path $Script)) {
    Write-Host "Error: Script '$Script' not found" -ForegroundColor Red
    Write-Host "Use -Help for usage information" -ForegroundColor Yellow
    exit 1
}

# Check if venv exists
if (!(Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run .\setup_and_test.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host "Generating artwork with $PaperSize paper size..." -ForegroundColor Cyan
Write-Host "Script: $Script" -ForegroundColor Gray
Write-Host "Paper: $PaperSize" -ForegroundColor Gray
Write-Host "Line Width: $LineWidth" -ForegroundColor Gray
if ($ShapeType) {
    Write-Host "Shape Type: $ShapeType" -ForegroundColor Gray
}
if ($GearMode) {
    Write-Host "Gear Mode: $GearMode" -ForegroundColor Gray
}
Write-Host "Count: $Count" -ForegroundColor Gray
Write-Host ""

$successCount = 0
for ($i = 1; $i -le $Count; $i++) {
    if ($Count -gt 1) {
        Write-Host "[$i/$Count] Generating..." -ForegroundColor Yellow
    }
    
    # Run the script with paper size, line width, shape type, and gear mode arguments
    # Arguments: open_file=False, svg=True, twitter=False, paper_size, line_width, shape_type/placement, gear_mode
    if ($ShapeType) {
        & ".\venv\Scripts\python.exe" $Script False True False $PaperSize $LineWidth $ShapeType 2>&1 | Out-Null
    } elseif ($GearMode) {
        $gearArgs = $GearMode -split ','
        if ($gearArgs.Count -eq 2) {
            & ".\venv\Scripts\python.exe" $Script False True False $PaperSize $LineWidth $gearArgs[0] $gearArgs[1] 2>&1 | Out-Null
        } else {
            & ".\venv\Scripts\python.exe" $Script False True False $PaperSize $LineWidth $GearMode 2>&1 | Out-Null
        }
    } else {
        & ".\venv\Scripts\python.exe" $Script False True False $PaperSize $LineWidth 2>&1 | Out-Null
    }
    
    if ($LASTEXITCODE -eq 0) {
        $successCount++
    } else {
        Write-Host "  Failed to generate image $i" -ForegroundColor Red
    }
}

Write-Host ""
if ($successCount -eq $Count) {
    Write-Host "✓ Successfully generated $successCount image(s)" -ForegroundColor Green
} else {
    Write-Host "⚠ Generated $successCount out of $Count image(s)" -ForegroundColor Yellow
}

$scriptName = [System.IO.Path]::GetFileNameWithoutExtension($Script)
$outputPath = "Images\$scriptName\0-svg\"
Write-Host "Files saved to: $outputPath" -ForegroundColor Cyan
