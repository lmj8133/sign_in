@echo off
REM Start the Flask-SocketIO server in a new command window.
start "" python main.py
REM Wait 3 seconds to allow the server to start (adjust if needed)
timeout /t 3
REM Open the default web browser to your app's URL.
start "" http://127.0.0.1:5000

