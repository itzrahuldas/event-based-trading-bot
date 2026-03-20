@echo off
echo ==========================================
echo Starting Frontend Dev Server
echo ==========================================
echo.

cd /d "%~dp0frontend"

echo Checking for Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install from: https://nodejs.org/
    pause
    exit /b 1
)

echo Checking for npm...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not found!
    pause
    exit /b 1
)

echo.
echo Installing dependencies (this may take 1-2 minutes)...
call npm install
if %errorlevel% neq 0 (
    echo.
    echo ERROR: npm install failed!
    pause
    exit /b 1
)

echo.
echo Starting Next.js dev server...
echo Frontend will be available at: http://localhost:3000
echo.
call npm run dev
