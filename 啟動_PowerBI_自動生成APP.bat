@echo off
chcp 65001 >nul
title Power BI Studio App - 專業儀表板自動生成中心
echo ======================================================================
echo   🚀 正在啟動 Power BI Studio App 視覺化自動生成系統...
echo   請稍候，瀏覽器將自動開啟操作畫面 (http://127.0.0.1:8765)
echo   (使用期間請勿關閉此黑底視窗)
echo ======================================================================
cd /d "%~dp0"
python "%~dp0PowerBI_Studio_App\app_server.py" 8765
pause
