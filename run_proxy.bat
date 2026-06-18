@echo off
setlocal

:: Arahkan ke direktori tempat file .bat ini berada (root proyek)
cd /d "%~dp0"

title Free Claude Code - Port 8082

echo ============================================
echo   Free Claude Code Proxy Server
echo   Direktori: %~dp0
echo   Running on http://localhost:8082
echo ============================================
echo.

:: Verifikasi uv tersedia
where uv >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 'uv' tidak ditemukan di PATH.
    echo Pastikan uv sudah terinstall: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

:: Verifikasi .env ada
if not exist "%~dp0.env" (
    echo [PERINGATAN] File .env tidak ditemukan di %~dp0
    echo Salin .env.example menjadi .env dan isi konfigurasi yang diperlukan.
    pause
    exit /b 1
)

echo [INFO] Memulai server...
echo [INFO] Tekan Ctrl+C untuk menghentikan server.
echo.

uv run uvicorn server:app --host 0.0.0.0 --port 8082 --timeout-graceful-shutdown 5

echo.
echo [INFO] Server telah berhenti.
pause
endlocal
