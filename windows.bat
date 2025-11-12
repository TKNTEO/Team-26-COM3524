@echo off
REM ============================
REM Run Teaching Tool Web Server on Windows with Docker
REM ============================

REM ---- CONFIG ----
set IMAGE_NAME=com3524
set DISPLAY=host.docker.internal:0.0

REM ---- BUILD IMAGE ----
echo Building Docker image...
docker build -t %IMAGE_NAME% .

REM ---- RUN CONTAINER ----
echo Running app on http://127.0.0.1:5000 ...
docker run -it ^
    -e DISPLAY=%DISPLAY% ^
    -p 5000:5000 ^
    %IMAGE_NAME% ^
    python3 run_tool.py

pause
