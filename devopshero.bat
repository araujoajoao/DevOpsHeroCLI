@echo off
rem DevOpsHeroCLI - Windows Launcher (CMD & PowerShell)
setlocal enabledelayedexpansion

cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python 3 nao foi encontrado no PATH.
    echo Baixe e instale o Python em https://www.python.org/downloads/
    echo Certifique-se de marcar a opcao "Add python.exe to PATH".
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [DevOpsHeroCLI] Primeira execucao detectada. Configurando ambiente virtual...
    python -m venv .venv
    echo [DevOpsHeroCLI] Instalando dependencias...
    .venv\Scripts\pip install --upgrade pip >nul 2>&1
    .venv\Scripts\pip install -e .
    echo [DevOpsHeroCLI] Ambiente configurado com sucesso!
)

if exist ".venv\Scripts\devopsherocli.exe" (
    .venv\Scripts\devopsherocli.exe %*
) else (
    .venv\Scripts\python.exe -m devopsherocli.cli %*
)
