<#
.SYNOPSIS
    dh - DevOpsHeroCLI ultra-fast 2-letter launcher for PowerShell
#>
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AppArgs
)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $ScriptDir "devopshero.ps1") @AppArgs
exit $LASTEXITCODE
