@echo off
echo Stopping Offline AI services...
taskkill /FI "WINDOWTITLE eq Offline AI Server*" /T /F >nul 2>&1
taskkill /IM llama-server.exe /F >nul 2>&1
echo Done.
pause
