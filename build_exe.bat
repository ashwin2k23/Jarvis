@echo off
echo Installing PyInstaller if needed...
pip install pyinstaller

echo Building Jarvis AI Executable...
pyinstaller --noconfirm run.spec

echo ========================================================
echo Build complete! Your executable folder is located in:
echo   dist\JarvisAI\JarvisAI.exe
echo ========================================================
pause
