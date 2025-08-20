"""
Optional health check server for platforms that require HTTP endpoints
(e.g., Replit, some monitoring services)
"""

from flask import Flask, jsonify
from threading import Thread
import os
from datetime import datetime

app = Flask(__name__)
start_time = datetime.utcnow()

@app.route('/')
def home():
    return jsonify({
        "status": "healthy",
        "service": "CustomGPT Discord Bot",
        "uptime": str(datetime.utcnow() - start_time)
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def start_health_server():
    """Start health check server in a separate thread"""
    server_thread = Thread(target=run)
    server_thread.daemon = True
    server_thread.start()

# Note: To use this, add to your bot.py:
# from health_check import start_health_server
# start_health_server()  # Before bot.run()