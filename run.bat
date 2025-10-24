@echo off
echo ====================================
echo RAG PDF System - Starting...
echo ====================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Streamlit application...
echo.
echo The application will open in your browser.
echo Press Ctrl+C to stop the server.
echo.

cd app
streamlit run streamlit_app.py

pause
