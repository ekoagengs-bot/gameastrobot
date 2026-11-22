@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name ASTROBOT-PC src\astrobot_pc.py
if errorlevel 1 goto :error
echo.
echo Build complete: dist\ASTROBOT-PC.exe
pause
exit /b 0
:error
echo Build failed. Check Python and internet connectivity.
pause
exit /b 1
