@echo off
:: Проверка инициализации Git
if not exist "%~dp0\.git" (
    echo [INFO] Initializing new Git repository...
    cd /d "%~dp0"
    git init
    git remote add origin https://github.com/IshushkaGit/LSCweb.git
    git fetch
    git checkout main
    if %ERRORLEVEL% neq 0 exit /b 1
)

:: Обычная процедура обновления
git pull origin main
if %ERRORLEVEL% neq 0 (
    git reset --hard origin/main
)
pause