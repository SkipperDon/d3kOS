"""
d3kOS Dashboard Server
Serves the main marine navigation hub at http://localhost:3000

Port assignments (from d3kos-config.env):
  Dashboard:    localhost:3000  (this app)
  Gemini Proxy: localhost:3001
  AI Bridge:    localhost:3002  (Phase 5)
  AvNav:        localhost:8080
  OpenPlotter:  localhost:8081  (infrastructure — not referenced here)
  Signal K:     localhost:8099
  Ollama:       192.168.1.36:11434 (LAN AI server)

CRITICAL: Signal K WebSocket is ws://localhost:8099 — NOT ws://localhost:3000.
"""
from flask import Flask, render_template, jsonify, request
import requests
import os
import shutil
import socket
import subprocess
from dotenv import load_dotenv

_cfg_dir = os.path.join(os.path.dirname(__file__), 'config')
load_dotenv(os.path.join(_cfg_dir, 'd3kos-config.env'))
# vessel.env is owner-config: VESSEL_NAME, HOME_PORT, UI_LANG — override if present
load_dotenv(os.path.join(_cfg_dir, 'vessel.env'), override=True)

app = Flask(__name__)

AVNAV_PORT    = os.getenv('AVNAV_PORT',    '8080')
GEMINI_PORT   = os.getenv('GEMINI_PORT',   '3001')
SIGNALK_PORT  = os.getenv('SIGNALK_PORT',  '8099')
OLLAMA_HOST   = os.getenv('OLLAMA_HOST',   '192.168.1.36:11434')
VESSEL_NAME   = os.getenv('VESSEL_NAME',   'MV SERENITY')
HOME_PORT_VAL = os.getenv('HOME_PORT',     'Home Port')
UI_LANG       = os.getenv('UI_LANG',       'en-GB')


def check_internet() -> bool:
    """Lightweight connectivity probe — no user data sent."""
    try:
        requests.get('http://captive.apple.com', timeout=3)
        return True
    except requests.RequestException:
        return False


def check_service(port: str) -> bool:
    """Return True if a local service answers on the given port."""
    try:
        requests.get(f'http://localhost:{port}', timeout=2)
        return True
    except requests.RequestException:
        return False


def check_ollama() -> bool:
    """Return True if the Ollama LAN server is reachable."""
    try:
        requests.get(f'http://{OLLAMA_HOST}/api/tags', timeout=3)
        return True
    except requests.RequestException:
        return False


@app.route('/')
def index():
    return render_template(
        'index.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        vessel_name=VESSEL_NAME,
        ui_lang=UI_LANG,
    )


@app.route('/status')
def status():
    """
    Live system status — polled by the frontend every 30 s.
    Checks: internet, AvNav (:8080), Gemini proxy (:3001),
            AI Bridge (:3002), Signal K (:8099), Ollama (LAN 192.168.1.36:11434).
    """
    return jsonify({
        'internet':  check_internet(),
        'avnav':     check_service(AVNAV_PORT),    # localhost:8080
        'gemini':    check_service(GEMINI_PORT),   # localhost:3001
        'ai_bridge': check_service('3002'),        # localhost:3002 (Phase 5)
        'signalk':   check_service(SIGNALK_PORT),  # localhost:8099
        'ollama':    check_ollama(),               # 192.168.1.36:11434
    })


@app.route('/settings')
def settings():
    """Settings & Help page — placeholder. Full build in Phase 4."""
    return render_template(
        'settings.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        signalk_port=SIGNALK_PORT,
        vessel_name=VESSEL_NAME,
        home_port=HOME_PORT_VAL,
    )


@app.route('/sysinfo')
def sysinfo():
    """
    Live system information for settings page Section 14.
    Uses only standard library — no extra dependencies.
    """
    # Disk usage
    try:
        usage = shutil.disk_usage('/')
        disk_pct = int(usage.used / usage.total * 100)
        disk_free_gb = round(usage.free / (1024 ** 3), 1)
    except Exception:
        disk_pct, disk_free_gb = 0, 0

    # Memory from /proc/meminfo
    mem_total = mem_avail = 0
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) // 1024
                elif line.startswith('MemAvailable:'):
                    mem_avail = int(line.split()[1]) // 1024
    except Exception:
        pass
    mem_pct = int((mem_total - mem_avail) / mem_total * 100) if mem_total else 0

    # CPU temperature (Pi-specific)
    cpu_temp = 'N/A'
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'],
            capture_output=True, text=True, timeout=3,
        )
        cpu_temp = result.stdout.strip().replace("temp=", "").replace("'C", " °C")
    except Exception:
        try:
            with open('/sys/class/thermal/thermal_zone0/temp') as f:
                cpu_temp = f"{int(f.read().strip()) / 1000:.1f} °C"
        except Exception:
            pass

    # Uptime
    uptime = 'N/A'
    try:
        with open('/proc/uptime') as f:
            secs = float(f.read().split()[0])
        h, m = int(secs // 3600), int((secs % 3600) // 60)
        uptime = f"{h}h {m}m"
    except Exception:
        pass

    # Local IP address
    ip = 'N/A'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
    except Exception:
        ip = socket.gethostname()

    return jsonify({
        'disk_pct':    disk_pct,
        'disk_free_gb': disk_free_gb,
        'mem_pct':     mem_pct,
        'mem_free_mb': mem_avail,
        'cpu_temp':    cpu_temp,
        'uptime':      uptime,
        'ip':          ip,
        'version':     'd3kOS v2.0',
    })


# Service name map — only these may be restarted via the API
_RESTART_SERVICES = {
    'signalk':    'signalk',
    'nodered':    'nodered',
    'dashboard':  'd3kos-dashboard',
    'gemini':     'd3kos-gemini',
    'ai_bridge':  'd3kos-ai-bridge',   # Phase 5
}


@app.route('/action/restart', methods=['POST'])
def action_restart():
    """
    System action: restart a named service via sudo systemctl.
    Body: {"service": "<key>"} where key is one of _RESTART_SERVICES.
    Requires: d3kos ALL=(ALL) NOPASSWD: /bin/systemctl restart <service>
              (add to /etc/sudoers.d/d3kos on Pi)
    """
    data = request.get_json(silent=True) or {}
    service = data.get('service', '')
    if service not in _RESTART_SERVICES:
        return jsonify({'ok': False, 'error': f'Unknown service: {service}'}), 400
    try:
        subprocess.run(
            ['sudo', 'systemctl', 'restart', _RESTART_SERVICES[service]],
            check=True, timeout=15, capture_output=True,
        )
        return jsonify({'ok': True, 'service': service})
    except subprocess.CalledProcessError as e:
        return jsonify({'ok': False, 'error': e.stderr.decode(errors='replace')}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/action/reboot', methods=['POST'])
def action_reboot():
    """
    System action: reboot the Pi. Requires sudo rights for systemctl reboot.
    """
    try:
        subprocess.Popen(['sudo', 'systemctl', 'reboot'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/offline')
def offline():
    return render_template('offline.html')


@app.route('/launch/opencpn', methods=['POST'])
def launch_opencpn():
    """
    Trigger OpenCPN via Node-RED.
    Proxies to existing Node-RED flow at localhost:1880/launch-opencpn
    (added in v0.9.2 — see nginx proxy block).
    """
    try:
        r = requests.post('http://127.0.0.1:1880/launch-opencpn', timeout=5)
        return jsonify({'ok': True, 'status': r.status_code})
    except requests.RequestException as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
