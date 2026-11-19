@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo       OFFLINE AI LAB CHATBOT
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found.
    echo Run the setup commands in README.md first.
    pause
    exit /b 1
)

if not exist "runtime\llama-server.exe" (
    echo ERROR: runtime\llama-server.exe is missing.
    echo Put the llama.cpp server executable in the runtime folder.
    pause
    exit /b 1
)

if not exist "models\model.gguf" (
    echo ERROR: models\model.gguf is missing.
    echo Put your GGUF model in the models folder and rename it to model.gguf
    pause
    exit /b 1
)

echo Starting local server...
start "Offline AI Server" /min ".venv\Scripts\python.exe" "server\main.py"

timeout /t 3 /nobreak >nul

echo.
echo Find this computer's LAN IPv4 address with:
ipconfig
echo.
echo Then clients should open:
echo http://HOST-IP:8000
echo.
echo Example:
echo http://192.168.1.100:8000
echo.
echo Internet is NOT required.
echo.
pause
