@echo off
echo ================================================
echo  Event-Based Trading Bot v4.0 - Frontend Setup
echo ================================================
echo.

REM Store the current directory
set "SCRIPT_DIR=%~dp0"

echo [Step 1/4] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from: https://nodejs.org/
    echo Then restart your terminal and run this script again.
    pause
    exit /b 1
)
echo SUCCESS: Node.js is installed
node --version

echo.
echo [Step 2/4] Checking npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not available
    pause
    exit /b 1
)
echo SUCCESS: npm is available
npm --version

echo.
echo [Step 3/4] Installing dependencies...
echo This may take 2-3 minutes on first run...
cd /d "%SCRIPT_DIR%frontend"
call npm install
if %errorlevel% neq 0 (
    echo.
    echo ERROR: npm install failed!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [Step 4/4] Starting Next.js development server...
echo.
echo ================================================
echo  Frontend will be available at:
echo  http://localhost:3000
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.
call npm run dev
