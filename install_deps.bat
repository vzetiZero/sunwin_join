@echo off
title Sunwin - Cai dat thu vien
cd /d "%~dp0"
echo ============================================================
echo   CAI DAT THU VIEN CHO TOOL GHEP BAN SUNWIN
echo   (websocket-client, msgpack, PySide6)
echo ============================================================
echo.

rem Uu tien trinh khoi dong 'py' neu co, neu khong dung 'python'
set "PY=python"
where py >nul 2>nul && set "PY=py -3"

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay Python trong PATH.
    echo Hay cai Python 3.10+ tai https://www.python.org/downloads/
    echo Nho tich "Add python.exe to PATH" khi cai roi chay lai file nay.
    echo.
    pause
    exit /b 1
)

echo [1/2] Nang cap pip...
%PY% -m pip install --upgrade pip
echo.
echo [2/2] Cai thu vien tu requirements.txt...
%PY% -m pip install -r "%~dp0requirements.txt"
echo.

echo ============================================================
echo   KIEM TRA:
%PY% -c "import websocket, msgpack, PySide6; print('OK: websocket-client, msgpack, PySide6')"
echo ============================================================
echo.
pause
