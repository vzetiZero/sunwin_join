@echo off
title Sunwin - Ghi goi WebSocket (tim join ngay)
cd /d "%~dp0"
echo ============================================================
echo   GHI GOI WEBSOCKET DE TIM PHUONG THUC "JOIN BAN NGAY"
echo   1) Vao SANH game  2) Enter (mark truoc)
echo   3) Bam CHƠI NHANH / VÀO BÀN  4) Enter (mark sau)  5) q = dung
echo ============================================================
echo.
echo (Neu muon dung lai profile da luu: sua dong duoi them --profile acc1)
echo.
python record_frames.py
echo.
echo (Xong. Xem file frames_*.jsonl va phan PHAN TICH o tren.)
pause
