# scripts/install_windows.ps1 - Instalador Nativo DevOpsHero para Windows (Desktop & Menu Iniciar)
param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path "$ScriptDir\..").Path
$IconPath = Join-Path $RepoRoot "assets\DevOpsHero.ico"
$LauncherBat = Join-Path $RepoRoot "dh.bat"
$LauncherPs1 = Join-Path $RepoRoot "dh.ps1"

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$StartMenuPath = [Environment]::GetFolderPath("Programs")

$DesktopShortcut = Join-Path $DesktopPath "DevOpsHero.lnk"
$StartMenuShortcut = Join-Path $StartMenuPath "DevOpsHero.lnk"

if ($Uninstall) {
    Write-Host "🗑️  Removendo atalhos do DevOpsHero..." -ForegroundColor Yellow
    if (Test-Path $DesktopShortcut) { Remove-Item $DesktopShortcut -Force }
    if (Test-Path $StartMenuShortcut) { Remove-Item $StartMenuShortcut -Force }
    Write-Host "✓ DevOpsHero desinstalado com sucesso." -ForegroundColor Green
    exit 0
}

Write-Host "⚡ [DevOpsHero Windows Installer] Configurando atalhos oficiais..." -ForegroundColor Cyan

# 1. Valida Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $PythonCmd) {
    Write-Host "⚠️  Python 3.9+ não detectado no PATH." -ForegroundColor Yellow
    Write-Host "   Instale com o winget: winget install Python.Python.3.12" -ForegroundColor Gray
}

# 2. Cria atalhos com WScript.Shell
$WshShell = New-Object -ComObject WScript.Shell

function Create-AppShortcut($Path) {
    $Shortcut = $WshShell.CreateShortcut($Path)
    $Shortcut.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $Shortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -Command `"cd '$RepoRoot'; .\dh.ps1`""
    $Shortcut.WorkingDirectory = $RepoRoot
    $Shortcut.Description = "DevOpsHero CLI - Terminal TUI RPG Game"
    if (Test-Path $IconPath) {
        $Shortcut.IconLocation = "$IconPath,0"
    }
    $Shortcut.Save()
}

Create-AppShortcut $DesktopShortcut
Create-AppShortcut $StartMenuShortcut

Write-Host "✓ Atalho criado na Área de Trabalho: $DesktopShortcut" -ForegroundColor Green
Write-Host "✓ Atalho criado no Menu Iniciar:     $StartMenuShortcut" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Agora você pode abrir o DevOpsHero clicando no ícone do Desktop ou pesquisando no Menu Iniciar!" -ForegroundColor Cyan
