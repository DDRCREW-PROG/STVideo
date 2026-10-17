@echo off
if exist "%~dp0STVideo.exe" (
  start "" "%~dp0STVideo.exe" "%~1" "%~dp0."
  exit /b
)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
  start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0tools\app.py" %*
  exit /b
)
echo Lancez INSTALLER-DEPENDANCES.cmd, ou utilisez la version autonome STVideo.exe.
pause
