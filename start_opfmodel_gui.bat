@echo off
setlocal

cd /d "%~dp0"

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

if not exist ".venv312\Scripts\python.exe" (
    echo [ERROR] Project virtual environment not found:
    echo         .venv312\Scripts\python.exe
    echo.
    echo Please create or restore the project virtual environment first.
    pause
    exit /b 1
)

".venv312\Scripts\python.exe" -c "import streamlit" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Streamlit is not installed in the project virtual environment.
    echo.
    echo Install GUI dependencies with:
    echo .\.venv312\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Starting OPFModel Selection GUI...
echo If the browser does not open automatically, use:
echo http://localhost:8501
echo.

".venv312\Scripts\python.exe" -m streamlit run "gui\OPFModel_Selection_GUI.py"

pause
