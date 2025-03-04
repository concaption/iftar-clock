@echo off
REM filepath: /C:/mydata/github/iftar-clock/install.bat
echo Iftar Clock - Installation Script
echo --------------------------------
echo.

REM Check if Python is installed
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7 or newer from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing required packages...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Installing PyInstaller...
python -m pip install pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install PyInstaller. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo All packages installed successfully.
echo.
echo Would you like to build the executable now? (Y/N)
set /p choice="> "

if /i "%choice%"=="Y" (
    echo.
    echo Building executable...
    python build_exe.py
) else (
    echo.
    echo Skipping build. You can build the executable later by running:
    echo python build_exe.py
)

echo.
echo Done.
pause