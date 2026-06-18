@echo off
title Free Claude Code Proxy - Port 8082
cd /d "D:\laragon\www\free-claude-code"
echo ============================================
echo   Free Claude Code Proxy Server
echo   Running on http://localhost:8082
echo ============================================
echo.
uv run uvicorn server:app --host 0.0.0.0 --port 8082 --timeout-graceful-shutdown 5
pause
