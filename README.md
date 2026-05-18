<div align="center">

```
  ╔══════════════════════════════════════════════╗
  ║        🌍  GEOLOCATION TRACKER CLI           ║
  ║     Windows  |  Linux  |  macOS  |  Termux   ║
  ╚══════════════════════════════════════════════╝
```

# 🌍 THE GEOLOCATION TRACKER

**A powerful terminal-based geo-tracking tool that captures precise GPS coordinates, device specifications, and network intelligence from any target — silently, via a single link.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![Ngrok](https://img.shields.io/badge/Ngrok-Free%20Tier-brightgreen?style=for-the-badge&logo=ngrok)](https://ngrok.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Termux-orange?style=for-the-badge)](https://github.com/palnirupam/THE-GEOLOCATION-TRACKER)
[![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)](LICENSE)

[📦 Installation](#-installation) • [🚀 Usage](#-usage) • [✨ Features](#-features) • [⚙️ Configuration](#%EF%B8%8F-configuration) • [📸 Output](#-sample-output)

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎯 **Precise GPS** | Two-step fix — fast cell-tower location first, then high-accuracy GPS |
| 🤖 **Bot Detection** | Filters WhatsApp/Telegram link previews — only real users trigger tracking |
| 📱 **Client Hints** | Bypasses Chrome's UA-freezing to get real Android version & device model |
| 🌐 **IP Intelligence** | ISP, carrier, VPN detection, city-level IP coordinates via ip-api.com |
| 🔗 **URL Shortening** | Auto-shortens ngrok link via shrtco.de for a cleaner, less suspicious URL |
| 🖼️ **Photo Lure** | Randomizes from 15 scenic photos each visit — looks like a real photo share |
| 📲 **WebView Detection** | Detects WhatsApp/Facebook in-app browser and shows "Open in Chrome" banner |
| 🔒 **HTTPS Only** | Ngrok tunnel enforces HTTPS — required for browser geolocation API |
| 🎨 **Animated CLI** | Typewriter-style banner with blinking SYSTEM READY indicator |
| 🖥️ **Cross-Platform** | Works on Windows, Linux, macOS, and Android (Termux) |

---

## 📋 Requirements

- Python 3.8+
- A free [Ngrok account](https://ngrok.com) (for public internet links)

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/palnirupam/THE-GEOLOCATION-TRACKER.git
cd THE-GEOLOCATION-TRACKER

# 2. Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Open `config.py` and set your values:

```python
# Get your free token from: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN = "your_token_here"

# Optional: Use a custom static domain (looks more legitimate)
# Get one free at: https://dashboard.ngrok.com/cloud-edge/domains
NGROK_DOMAIN = ""   # e.g. "photo-share-app.ngrok-free.app"
```

> **Note:** `config.py` is listed in `.gitignore` — your token will never be pushed to GitHub.

---

## 🚀 Usage

```bash
python server.py
```

You will see:

```
  ╔══════════════════════════════════════════════╗
  ║        🌍  GEOLOCATION TRACKER CLI           ║
  ║     Windows  |  Linux  |  macOS  |  Termux   ║
  ╚══════════════════════════════════════════════╝
  ● SYSTEM READY

Select Connection Type:
  [1] Localhost  (same network / testing)
  [2] Ngrok      (public internet link)

Enter choice (1/2):
```

Choose **`2`** for a public link, then send it to the target.

```
  ╔══════════════════════════════════════════════╗
  ║   🎯  LINK READY — SEND TO TARGET           ║
  ╚══════════════════════════════════════════════╝

  📎 SHORT ▶  https://9qr.de/ab3x
  🔗 FULL  ▶  https://photo-share-app.ngrok-free.app/photo/ID
```

---

## 📸 Sample Output

When the target opens the link:

```
====================================================
  [+] TARGET OPENED THE LINK!
====================================================
 ┣━ IP Address  : 2409:40e0:XXXX:XXXX::1
 ┣━ Device      : 📱 Mobile
 ┣━ OS          : Android 16.0.0
 ┣━ Browser     : Chrome Mobile 148.0.0
 ┣━ ISP/Carrier : Reliance Jio Infocomm Limited
 ┣━ Network     : 📶 Mobile Data
 ┣━ Org         : Reliance Jio Infocomm Limited
 ┣━ City        : Kolkata, West Bengal, India
 ┣━ IP Coords   : 22.5643, 88.3693
 ┗━ Maps (IP)   : https://maps.google.com/?q=22.5643,88.3693

[*] Waiting for GPS permission from target...

[📱] DEVICE DETAILS:
 ┣━ Screen      : 412x919 (24bit)
 ┣━ Model       : AIN065
 ┣━ Architecture: arm64
 ┣━ Language    : en-IN
 ┣━ Timezone    : Asia/Calcutta
 ┣━ Network     : 5G | 78 Mbps | type=cellular
 ┣━ Battery     : 87% 🔋Not Charging
 ┣━ CPU Cores   : 8
 ┗━ RAM         : 8GB

[★ GPS - FAST]
 ┣━ Latitude    : 22.572600
 ┣━ Longitude   : 88.363900
 ┣━ Accuracy    : ±150 meters
 ┗━ Google Maps : https://maps.google.com/?q=22.572600,88.363900

[★ GPS - ACCURATE]
 ┣━ Latitude    : 22.572938
 ┣━ Longitude   : 88.364122
 ┣━ Accuracy    : ±8 meters
 ┗━ Google Maps : https://maps.google.com/?q=22.572938,88.364122
```

---

## 🔧 How It Works

```
Target clicks link
      ↓
[Bot Check] — WhatsApp/Telegram crawlers get empty 404
      ↓
[Step 1] Server sends Accept-CH headers → 302 Redirect
      ↓
[Step 2] Chrome sends real Client Hints (true Android version, model)
      ↓
[IP Lookup] → ISP, carrier, VPN flag, city via ip-api.com
      ↓
[Page Loads] → Blurred photo with "View Full Image" button
      ↓
Target clicks button → GPS permission dialog appears
      ↓
[GPS FAST]    Cell-tower location sent instantly (2-3 sec)
[GPS ACCURATE] Satellite GPS sent in background (10-20 sec)
```

---

## ⚠️ Known Limitations

| Limitation | Reason |
|---|---|
| RAM capped at 8GB | Chrome privacy sandbox — cannot be bypassed |
| GPS requires user Allow | Cannot be bypassed — browser security policy |
| IP location ≈ city-level | ISPs use shared gateways, not exact addresses |
| Brave browser blocks everything | Brave shields block GPS, battery, network APIs |
| GPS blocked if previously denied | Chrome remembers per-domain. Fix: Incognito mode |

---

## 💡 Tips

- 🔒 **GPS not showing?** → Tell the target to open the link in **Chrome Incognito** mode
- 📌 **Better domain?** → Set a [free ngrok static domain](https://dashboard.ngrok.com/cloud-edge/domains) in `config.py`
- 🔄 **Tunnel expired?** → Free ngrok tunnels reset every 8 hours — just restart `python server.py`
- 🚫 **Token invalid?** → Get a new one at [ngrok dashboard](https://dashboard.ngrok.com/authtokens) and update `config.py`

---

## 📁 Project Structure

```
THE-GEOLOCATION-TRACKER/
├── server.py          # Main CLI application
├── config.py          # Your ngrok token & settings
├── requirements.txt   # Python dependencies
└── .gitignore
```

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

> ⚠️ **Disclaimer:** This tool is for **educational and authorized testing purposes only**. The author is not responsible for any misuse. Always obtain permission before tracking any individual.

---

<div align="center">

Made with ❤️ by [palnirupam](https://github.com/palnirupam)

⭐ Star this repo if you found it useful!

</div>
