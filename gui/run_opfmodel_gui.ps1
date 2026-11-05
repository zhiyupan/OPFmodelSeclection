$ErrorActionPreference = "Stop"

[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$Python = Join-Path $ProjectRoot ".venv312\Scripts\python.exe"
$App = Join-Path $ScriptDir "OPFModel_Selection_GUI.py"
$Requirements = Join-Path $ProjectRoot "requirements.txt"

if (-not (Test-Path $Python)) {
    Write-Host "Project Python was not found: $Python"
    exit 1
}

& $Python -c "import streamlit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Streamlit is not installed in .venv312."
    Write-Host "Install it first:"
    Write-Host "  `"$Python`" -m pip install -r `"$Requirements`""
    exit 1
}

& $Python -m streamlit run $App
