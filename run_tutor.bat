@echo off
chcp 65001 > nul
echo =======================================================
echo  Starting VerbaFlow AI - English Voice Coach
echo =======================================================
start http://127.0.0.1:8766/
python server.py
pause
