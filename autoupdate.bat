@echo off
:: LSCweb AutoUpdater - fixed version
title LSCweb AutoUpdater
color 0A

echo [INFO] Checking for LSCweb updates...
echo.

:: Check if Git is installed
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH
    pause
    exit /b 1
)

:: Main update logic - FIXED PATH HANDLING
cd /D "%~dp0"
git pull https://github.com/IshushkaGit/LSCweb.git 2>NUL
if %ERRORLEVEL% == 0 goto :success

echo [WARN] Update failed, performing hard reset...
git reset --hard
git pull https://github.com/IshushkaGit/LSCweb.git

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to update repository
    echo.
    echo Possible solutions:
    echo 1. Check your internet connection
    echo 2. Verify repository path: %~dp0
    echo 3. Delete folder and clone fresh: git clone https://github.com/IshushkaGit/LSCweb.git
    pause
    exit /b 1
)

:success
echo [INFO] Repository updated successfully
echo.

:: Install/update dependencies
echo [INFO] Checking dependencies...
call install_dependencies.bat

echo.
echo [INFO] Starting application...
start.bat

pause