@echo off
rem ساخت فایل exe مستقل در پوشهٔ dist
cd /d "%~dp0"

python -m pip install --upgrade --quiet pyinstaller openpyxl pystray Pillow
if errorlevel 1 goto :error

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name WorkingHour ^
    --hidden-import pystray._win32 ^
    --exclude-module pytest --exclude-module unittest --exclude-module pydoc ^
    app.py
if errorlevel 1 goto :error

echo.
echo ساخته شد: dist\WorkingHour.exe
pause
exit /b 0

:error
echo.
echo ساخت فایل با خطا تمام شد.
pause
exit /b 1
