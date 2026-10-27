<#
.SYNOPSIS
    DevOpsHeroCLI - Native PowerShell Launcher (dh.ps1)

.DESCRIPTION
    Launcher oficial e compacto para execução do DevOpsHeroCLI no PowerShell
    (Windows PowerShell 5.1 e PowerShell 7+ Core no Windows, macOS ou Linux).
    Detecta ambiente virtual, instala dependências e inicia o simulador.
#>

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AppArgs
)

# Configura encoding UTF-8
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    $OutputEncoding           = [System.Text.Encoding]::UTF8
} catch {
    # Suprime caso console não suporte alteração
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir

# Exporta marcador de shell
$env:DEVOPSHERO_SHELL = "powershell"

# Easter-egg bem-humorado
Write-Host ""
Write-Host "========================================================================" -ForegroundColor DarkYellow
Write-Host " ⚠️   ALERTA DE SEGURANÇA MENTAL: PowerShell Detectado!" -ForegroundColor Yellow
Write-Host " Você realmente chama o PowerShell de terminal?! 😂" -ForegroundColor White
Write-Host " Recomendamos fortemente um terminal de verdade (bash/zsh) longe do Windows! 🐧" -ForegroundColor Cyan
Write-Host " Mas relaxa: o DevOpsHero roda suave até aqui. Bons estudos, herói!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor DarkYellow
Write-Host ""

# Verifica Python
$PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command "py" -ErrorAction SilentlyContinue
}

if (-not $PythonCmd) {
    Write-Host "[ERRO] Python 3 não foi encontrado no PATH." -ForegroundColor Red
    Write-Host "Por favor, instale o Python 3.9+ em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Certifique-se de marcar a opção 'Add python.exe to PATH' durante a instalação." -ForegroundColor Yellow
    exit 1
}

$VenvDir = Join-Path $ScriptDir ".venv"
$VenvPython = if ($IsWindows -or ($env:OS -like "*Windows*")) {
    Join-Path $VenvDir "Scripts\python.exe"
} else {
    Join-Path $VenvDir "bin/python"
}

$VenvPip = if ($IsWindows -or ($env:OS -like "*Windows*")) {
    Join-Path $VenvDir "Scripts\pip.exe"
} else {
    Join-Path $VenvDir "bin/pip"
}

# Configura ambiente virtual se não existir
if (-not (Test-Path $VenvPython)) {
    Write-Host "[DevOpsHeroCLI] Configurando ambiente virtual (.venv)..." -ForegroundColor Cyan
    & $PythonCmd.Source -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha ao criar ambiente virtual." -ForegroundColor Red
        exit 1
    }

    Write-Host "[DevOpsHeroCLI] Instalando dependências..." -ForegroundColor Cyan
    & $VenvPip install --upgrade pip --quiet
    & $VenvPip install -e .
    Write-Host "[DevOpsHeroCLI] Ambiente configurado com sucesso!" -ForegroundColor Green
}

# Inicia DevOpsHeroCLI
if ($AppArgs) {
    & $VenvPython -m devopsherocli.cli @AppArgs
} else {
    & $VenvPython -m devopsherocli.app
}

exit $LASTEXITCODE
