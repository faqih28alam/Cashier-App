param(
    [string]$InstallDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'

$url     = 'https://github.com/faqih28alam/Cashier-App/archive/refs/heads/main.zip'
$zipPath = "$env:TEMP\cashier_update.zip"
$tmpDir  = "$env:TEMP\cashier_update_tmp"

Write-Host "  Downloading from GitHub..."
Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

Write-Host "  Extracting..."
if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force

$src = Join-Path $tmpDir "Cashier-App-main"

# Files to never overwrite (client-specific data and config)
$preserve = @(
    'backend\cashier.db',
    'backend\.env',
    'frontend\.env.local'
)

# Directory prefixes to skip entirely (large generated dirs and uploaded assets)
$skipDirs = @(
    'frontend\node_modules',
    'frontend\.next',
    'backend\static'
)

Write-Host "  Applying update (preserving database and settings)..."

Get-ChildItem -Path $src -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($src.Length + 1)

    # Skip preserved files
    if ($preserve -contains $rel) { return }

    # Skip generated/uploaded directories
    foreach ($dir in $skipDirs) {
        if ($rel.StartsWith($dir + '\')) { return }
    }

    $dest    = Join-Path $InstallDir $rel
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item -Path $_.FullName -Destination $dest -Force
}

Write-Host "  Cleaning up..."
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
Remove-Item $tmpDir  -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "  Done."
