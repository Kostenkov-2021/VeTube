# Build script for VeTube
# Runs cxfreeze build and removes duplicate sound_lib DLLs

Write-Host "=== Building VeTube ===" -ForegroundColor Cyan

# Clean previous builds
Remove-Item -Recurse -Force build, build2 -ErrorAction SilentlyContinue

# Run cxfreeze build
uv run cxfreeze build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build FAILED" -ForegroundColor Red
    exit 1
}

# Remove duplicate sound_lib DLLs
# cx_Freeze copies sound_lib package to lib/sound_lib/ including the lib/ subdirectory with DLLs
# Our include_files already puts DLLs in sound_lib/lib/ (where paths.py expects them)
# So we remove the duplicate at lib/sound_lib/lib/
$duplicatePath = "build\exe.win-amd64-3.14\lib\sound_lib\lib"
if (Test-Path $duplicatePath) {
    Remove-Item -Recurse -Force $duplicatePath
    Write-Host "Removed duplicate: $duplicatePath" -ForegroundColor Yellow
}

# Calculate final size
$size = (Get-ChildItem -Recurse build -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($size / 1MB, 2)
Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "Size: $sizeMB MB" -ForegroundColor Green
