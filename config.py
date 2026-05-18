"""
Geolocation Tracker — Configuration
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
NGROK_AUTHTOKEN = ""   # Paste your token here: https://dashboard.ngrok.com/authtokens

# Optional: Set a custom static ngrok domain (looks more real)
# Get ONE free static domain at: https://dashboard.ngrok.com/cloud-edge/domains
# Example: NGROK_DOMAIN = "photo-viewer-app.ngrok-free.app"
# Leave empty → ngrok gives random domain each time
NGROK_DOMAIN = ""
