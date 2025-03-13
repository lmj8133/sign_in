# main.py
import subprocess
import time

# Start the Flask app
flask_process = subprocess.Popen(["python", "app.py"])
time.sleep(2)  # Wait briefly for Flask to start

# Start Cloudflare Tunnel (ensure the full path for cloudflared is correct)
tunnel_process = subprocess.Popen(["/usr/local/bin/cloudflared", "tunnel", "--url", "http://0.0.0.0:3000"])

# Wait for both processes to finish
flask_process.wait()
tunnel_process.wait()

