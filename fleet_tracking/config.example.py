"""
Geolocation Tracker — Configuration Template

SETUP INSTRUCTIONS:
1. Copy this file → rename it to  config.py
2. Fill in your NGROK_AUTHTOKEN below
3. Run: python server.py
"""

# ==========================================
# SERVER SETTINGS
# ==========================================
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080


# ==========================================
# NGROK SETTINGS
# ==========================================

# Get your free authtoken from:
# https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN = ""   # ← Paste your token here

# Optional: Use a custom static domain (looks more legitimate)
# Get ONE free static domain at: https://dashboard.ngrok.com/cloud-edge/domains
# Example: NGROK_DOMAIN = "photo-viewer-app.ngrok-free.app"
NGROK_DOMAIN = ""
