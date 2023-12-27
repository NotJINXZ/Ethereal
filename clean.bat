@echo off
setlocal enabledelayedexpansion

rem Prevent the creation of __pycache__ folders
set PYTHONDONTWRITEBYTECODE=1

rem Delete existing __pycache__ folders
for /d /r %%i in (__pycache__) do (
    rd /s /q "%%i"
)

echo Cleanup completed.
