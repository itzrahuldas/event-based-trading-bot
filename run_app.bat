@echo off
setlocal
echo ==========================================
echo Starting Event-Based Trading Bot v4.0
echo ==========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check for npm
call npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed or not in PATH.
    echo Please make sure npm is included with your Node.js installation.
    pause
    exit /b 1
)

echo.
echo [1/3] Installing/Verifying Backend Dependencies...
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing backend dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing/Verifying Frontend Dependencies...
cd frontend
if not exist node_modules (
    echo Installing node modules...
    call npm install
    if %errorlevel% neq 0 (
        echo Error: 'npm install' failed.
        echo Please check your internet connection or npm configuration.
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Node modules found. Skipping install.
)
cd ..

echo.
echo [3/3] Launching Services...
echo.
echo Starting Backend Server (new window)...
start "Trading Bot Backend" cmd /k "uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000"

echo Starting Frontend Dev Server (new window)...
cd frontend
REM Use 'call' to ensure we catch if it fails immediately, though start launches async.
REM We launch it in a new window that keeps open on error.
start "Trading Bot Frontend" cmd /k "npm run dev || echo Frontend failed to start! & pause"
cd ..

echo.
echo ==========================================
echo Application is running!
echo Backend API Docs: http://localhost:8000/docs
echo Frontend UI:      http://localhost:3000
echo ==========================================
echo.
echo Press any key to close this launcher (services will keep running)...
pause >nul
