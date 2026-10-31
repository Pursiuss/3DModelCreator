@echo off
rem Starts the local 3D model viewer and opens it in the browser.
rem Double-click this file; close the window (or press Ctrl+C) to stop the viewer.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo The kit's Python environment is missing. Set it up first, from this folder:
    echo     python -m venv .venv
    echo     .venv\Scripts\python -m pip install -r skill\requirements.txt
    pause
    exit /b 1
)

rem open the page once the server has had a moment to start
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8765"
echo Model viewer at http://localhost:8765 - press Reload in the page after a new run.
echo Close this window to stop it.
".venv\Scripts\python.exe" tests\viewer\serve.py --port 8765
pause
