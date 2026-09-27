@echo off
title Sunwin Headless - Ghep 2 acc
cd /d "%~dp0"
echo ============================================================
echo   GHEP 2 TAI KHOAN (khong can trinh duyet)
echo   acc1 tao ban mo -^> acc2 vao ngay
echo ============================================================
python sunwin_headless.py auth_acc1.json auth_acc2.json 100 1 2
echo.
echo (Xong. Xem log chi tiet trong pair_log.txt)
pause
