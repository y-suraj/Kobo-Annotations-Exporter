@echo off
cd /d "%~dp0"
py -3 kobo_to_html.py
if errorlevel 1 pause
