@echo off
cd /d "%~dp0"
py -3.12 -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Installation terminee. Lancez ENCODER.cmd.
pause
exit /b 0
:error
echo Installation impossible. Installez Python 3.12 x64 avec Tkinter, ou utilisez STVideo.exe.
pause
exit /b 1
