@echo off
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error installing dependencies. Please ensure Python and Pip are installed and in your PATH.
    pause
    exit /b %errorlevel%
)

echo Starting Dashboard...
streamlit run src\dashboard.py
pause
