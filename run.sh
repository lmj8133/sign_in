#!/bin/bash
# Launch the Flask-SocketIO server in the background.
python3 ./main.py &

# Wait a few seconds for the server to start.
sleep 3

# Open the default web browser to the app URL.
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  open http://127.0.0.1:3000
else
  # Linux
  xdg-open http://127.0.0.1:3000
fi

