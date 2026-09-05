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
from flask import Flask, render_template, jsonify, request, redirect
import json
import os
import sys
import hashlib
import shutil
import socket
import sqlite3
import subprocess
import requests
from pathlib import Path
import datetime
from dotenv import load_dotenv

_cfg_dir = os.path.join(os.path.dirname(__file__), 'config')
_VESSEL_ENV_PATH = os.path.join(_cfg_dir, 'vessel.env')
_APIKEYS_ENV_PATH = os.path.join(_cfg_dir, 'api-keys.env')  # gitignored — Gemini key etc.
load_dotenv(os.path.join(_cfg_dir, 'd3kos-config.env'))
# vessel.env is owner-config: VESSEL_NAME, HOME_PORT, UI_LANG — override if present
load_dotenv(_VESSEL_ENV_PATH, override=True)
# api-keys.env holds sensitive keys (never committed) — override if present
load_dotenv(_APIKEYS_ENV_PATH, override=True)

ONBOARDING_RUN_LIMIT = 10
ONBOARDING_FILE = '/opt/d3kos/config/onboarding.json'


def _password_changed() -> bool:
    """Return True if the d3kos user has changed the default password."""
    try:
        with open(ONBOARDING_FILE) as f:
            return json.load(f).get('password_changed', False)
    except Exception:
        return False


def _get_device_uuid() -> str:
    """Return a stable device ID for mobile pairing.
    Reads /etc/machine-id (Pi-standard); falls back to hostname hash."""
    try:
        with open('/etc/machine-id') as f:
            mid = f.read().strip()
        if len(mid) >= 32:
            return (
                f'{mid[0:8]}-{mid[8:12]}-{mid[12:16]}-'
                f'{mid[16:20]}-{mid[20:32]}'
            ).upper()
    except Exception:
        pass
    raw = hashlib.sha256(socket.gethostname().encode()).hexdigest()
    return (
        f'{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-'
        f'{raw[16:20]}-{raw[20:32]}'
    ).upper()

app = Flask(__name__)

AVNAV_PORT    = os.getenv('AVNAV_PORT',    '8080')
GEMINI_PORT   = os.getenv('GEMINI_PORT',   '3001')
SIGNALK_PORT  = os.getenv('SIGNALK_PORT',  '8099')
OLLAMA_HOST   = os.getenv('OLLAMA_HOST',   '127.0.0.1:11434')
VESSEL_NAME   = os.getenv('VESSEL_NAME',   'MV SERENITY')
HOME_PORT_VAL = os.getenv('HOME_PORT',     'Home Port')
UI_LANG       = os.getenv('UI_LANG',       'en-GB')
HOME_PORT_LAT = os.getenv('HOME_PORT_LAT', '')
HOME_PORT_LON = os.getenv('HOME_PORT_LON', '')


def check_internet() -> bool:
    """Lightweight connectivity probe — no user data sent."""
    try:
        requests.get('http://captive.apple.com', timeout=3)
        return True
    except requests.RequestException:
        return False


def check_service(port: str) -> bool:
    """Return True if a local service answers without a server error.

    BUG-50 defect 4: the previous version caught only RequestException, so a
    service returning HTTP 500 was reported as up.

    A 2xx-only rule is WRONG here and was corrected during S117 validation:
    ai-bridge on :3002 returns 404 on "/" while answering 200 on /anchor/state,
    so 2xx-only reported a healthy service as down. 4xx means the server is
    there and answered; only 5xx means it is broken.
    """
    try:
        r = requests.get(f'http://localhost:{port}', timeout=2)
        return r.status_code < 500
    except requests.RequestException:
        return False


def _sk_age_seconds(timestamp):
    """Age in seconds of a Signal K ISO-8601 timestamp, or None if unparseable."""
    if not timestamp:
        return None
    try:
        if str(timestamp).endswith('Z'):
            timestamp = str(timestamp)[:-1] + '+00:00'
        dt = datetime.datetime.fromisoformat(str(timestamp))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()
    except (ValueError, TypeError):
        return None


def check_gps():
    """True only if Signal K holds a position that is BOTH present and fresh (<=10s).

    BUG-50 defect 1: presence of a running Signal K server says nothing about
    whether a GPS exists. Stale data must read False.
    """
    try:
        r = requests.get(
            f'http://localhost:{SIGNALK_PORT}/signalk/v1/api/vessels/self/navigation/position',
            timeout=3)
        if r.status_code == 200:
            data = r.json()
            value = data.get('value') if isinstance(data, dict) else None
            if isinstance(value, dict) and value.get('latitude') is not None \
                    and value.get('longitude') is not None:
                age = _sk_age_seconds(data.get('timestamp'))
                return age is not None and age <= 10
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        pass
    return False


def check_ais():
    """Three-state AIS health: 'receiving' | 'no_targets' | 'no_data'.

    'no_targets' is neither healthy nor a fault: nothing in range is normal at
    sea, and Signal K cannot distinguish that from a dead receiver. Never green.
    """
    try:
        r = requests.get(f'http://localhost:{SIGNALK_PORT}/signalk/v1/api/vessels/', timeout=3)
        if r.status_code != 200:
            return 'no_data'
        vessels = r.json()
        if not isinstance(vessels, dict):
            return 'no_data'

        self_id = ''
        try:
            sr = requests.get(f'http://localhost:{SIGNALK_PORT}/signalk/v1/api/self', timeout=3)
            if sr.status_code == 200:
                # /api/self returns "vessels.urn:mrn:..." but the vessel KEYS carry
                # no "vessels." prefix. An exact match therefore never fires, and own
                # ship gets counted as an AIS target the moment it has a GPS fix.
                self_id = sr.text.strip().strip('"')
                if self_id.startswith('vessels.'):
                    self_id = self_id[len('vessels.'):]
        except (requests.RequestException, ValueError):
            pass

        for vessel_id, vessel in vessels.items():
            if self_id and (vessel_id == self_id or self_id.endswith(vessel_id)):
                continue
            if not isinstance(vessel, dict):
                continue
            pos = (vessel.get('navigation') or {}).get('position') or {}
            age = _sk_age_seconds(pos.get('timestamp')) if isinstance(pos, dict) else None
            if age is not None and age <= 300:
                return 'receiving'
        return 'no_targets'
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        return 'no_data'


def check_avnav():
    """(healthy, chart_count) from AvNav's OWN status API.

    BUG-50 defect 3: a bare port probe passes with an expired chart licence and
    zero charts loaded -- the exact OB-O05 state.
    """
    try:
        r = requests.get(
            f'http://localhost:{AVNAV_PORT}/viewer/avnav_navi.php?request=status',
            timeout=3)
        if r.status_code != 200:
            return False, None
        data = r.json()
        if not isinstance(data, dict) or not isinstance(data.get('handler'), list):
            return False, None
        chart_count = 0
        for handler in data['handler']:
            if not isinstance(handler, dict) or handler.get('name') != 'ChartHandler':
                continue
            items = (handler.get('info') or {}).get('items') or []
            for item in items:
                text = str((item or {}).get('info', ''))
                parts = text.replace(',', ' ').split()
                for i, part in enumerate(parts):
                    if part.startswith('chart') and i > 0 and parts[i - 1].isdigit():
                        chart_count += int(parts[i - 1])
        return True, chart_count
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        return False, None


def check_ollama() -> bool:
    """Return True if the Ollama LAN server is reachable."""
    try:
        requests.get(f'http://{OLLAMA_HOST}/api/tags', timeout=3)
        return True
    except requests.RequestException:
        return False


@app.route('/')
def index():
    # First-run: show onboarding wizard if vessel.env is missing
    if not os.path.exists(_VESSEL_ENV_PATH):
        return redirect('/setup')
    # Security gate: force password change if still default
    if not _password_changed():
        return redirect('/setup?require_password=1')
    return render_template(
        'index.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        vessel_name=VESSEL_NAME,
        ui_lang=UI_LANG,
    )


@app.route('/setup', methods=['GET'])
def setup_get():
    """Onboarding wizard — 6 steps."""
    run_count = int(os.getenv('ONBOARDING_RUNS', '0'))
    return render_template(
        'setup.html',
        error=None,
        run_count=run_count,
        run_limit=ONBOARDING_RUN_LIMIT,
        device_uuid=_get_device_uuid(),
    )


@app.route('/setup', methods=['POST'])
def setup_post():
    """Save wizard data and redirect to dashboard."""
    global VESSEL_NAME, HOME_PORT_VAL, UI_LANG
    vessel_name     = request.form.get('vessel_name', '').strip()
    home_port       = request.form.get('home_port', '').strip()
    ui_lang         = request.form.get('ui_lang', 'en-GB').strip()
    gemini_key      = request.form.get('gemini_api_key', '').strip()

    # Vessel particulars
    boat_make       = request.form.get('boat_make', '').strip()
    boat_year       = request.form.get('boat_year', '').strip()
    boat_model      = request.form.get('boat_model', '').strip()
    boat_type       = request.form.get('boat_type', '').strip()
    boat_loa        = request.form.get('boat_loa', '').strip()
    boat_region     = request.form.get('boat_region', '').strip()

    # Engine 1
    engine_make     = request.form.get('engine_make', '').strip()
    engine_model    = request.form.get('engine_model', '').strip()
    engine_year     = request.form.get('engine_year', '').strip()
    engine_hp       = request.form.get('engine_hp', '').strip()
    engine_cylinders= request.form.get('engine_cylinders', '').strip()
    engine_fuel     = request.form.get('engine_fuel', '').strip()
    engine_induction= request.form.get('engine_induction', '').strip()
    engine_idle_rpm = request.form.get('engine_idle_rpm', '').strip()
    engine_max_rpm  = request.form.get('engine_max_rpm', '').strip()
    engine_count    = request.form.get('engine_count', '1').strip()

    # Engine 2 (twin only)
    engine2_make    = request.form.get('engine2_make', '').strip()
    engine2_model   = request.form.get('engine2_model', '').strip()
    engine2_year    = request.form.get('engine2_year', '').strip()

    # Electronics
    nmea_gateway    = request.form.get('nmea_gateway', '').strip()
    chartplotter    = request.form.get('chartplotter', '').strip()
    vhf_radio       = request.form.get('vhf_radio', '').strip()

    run_count = int(os.getenv('ONBOARDING_RUNS', '0')) + 1

    if not vessel_name:
        return render_template(
            'setup.html', error='Vessel name is required.',
            run_count=run_count - 1, run_limit=ONBOARDING_RUN_LIMIT,
            device_uuid=_get_device_uuid(),
        )

    # Write vessel.env (non-sensitive owner config)
    os.makedirs(_cfg_dir, exist_ok=True)
    vessel_data = {
        'VESSEL_NAME':       vessel_name,
        'HOME_PORT':         home_port,
        'UI_LANG':           ui_lang,
        'ONBOARDING_RUNS':   str(run_count),
        'BOAT_MAKE':         boat_make,
        'BOAT_YEAR':         boat_year,
        'BOAT_MODEL':        boat_model,
        'BOAT_TYPE':         boat_type,
        'BOAT_LOA':          boat_loa,
        'BOAT_REGION':       boat_region,
        'ENGINE_MAKE':       engine_make,
        'ENGINE_MODEL':      engine_model,
        'ENGINE_YEAR':       engine_year,
        'ENGINE_HP':         engine_hp,
        'ENGINE_CYLINDERS':  engine_cylinders,
        'ENGINE_FUEL':       engine_fuel,
        'ENGINE_INDUCTION':  engine_induction,
        'ENGINE_IDLE_RPM':   engine_idle_rpm,
        'ENGINE_MAX_RPM':    engine_max_rpm,
        'ENGINE_COUNT':      engine_count,
        'ENGINE2_MAKE':      engine2_make,
        'ENGINE2_MODEL':     engine2_model,
        'ENGINE2_YEAR':      engine2_year,
        'NMEA_GATEWAY':      nmea_gateway,
        'CHARTPLOTTER':      chartplotter,
        'VHF_RADIO':         vhf_radio,
    }
    with open(_VESSEL_ENV_PATH, 'w') as f:
        for k, v in vessel_data.items():
            if v:  # skip empty fields — avoids blank lines in env file
                f.write(f'{k}={v}\n')

    # Write api-keys.env (gitignored — Gemini key only written if provided)
    if gemini_key:
        with open(_APIKEYS_ENV_PATH, 'w') as f:
            f.write(f'GEMINI_API_KEY={gemini_key}\n')

    # Reload runtime values without restarting Flask
    load_dotenv(_VESSEL_ENV_PATH, override=True)
    if gemini_key:
        load_dotenv(_APIKEYS_ENV_PATH, override=True)
    VESSEL_NAME   = os.getenv('VESSEL_NAME',  vessel_name)
    HOME_PORT_VAL = os.getenv('HOME_PORT',    home_port)
    UI_LANG       = os.getenv('UI_LANG',      ui_lang)

    return redirect('/')


@app.route('/network/check-default-password', methods=['GET'])
def check_default_password():
    """Returns {default: true} if the d3kos password has not been changed yet."""
    return jsonify({'default': not _password_changed()})


@app.route('/network/change-password', methods=['POST'])
def change_password():
    """Change the d3kos system password. Writes flag to onboarding.json on success."""
    data = request.get_json(silent=True) or {}
    new_password = data.get('new_password', '').strip()

    if not new_password or len(new_password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400

    # BUG-107 follow-up (S148): the UI hint claims this, but nothing enforced it.
    if new_password == 'd3kos2026':
        return jsonify({'success': False, 'error': 'Cannot reuse the factory default password'}), 400

    try:
        result = subprocess.run(
            ['sudo', '/usr/sbin/chpasswd'],
            input=f'd3kos:{new_password}\n',
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr.strip()}), 500

        # Mark password changed in onboarding.json
        try:
            with open(ONBOARDING_FILE) as f:
                onboarding = json.load(f)
        except Exception:
            onboarding = {}
        onboarding['password_changed'] = True
        os.makedirs(os.path.dirname(ONBOARDING_FILE), exist_ok=True)
        with open(ONBOARDING_FILE, 'w') as f:
            json.dump(onboarding, f, indent=2)

        return jsonify({'success': True})
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout changing password'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/status')
def status():
    """
    Live system status — polled by the frontend every 30 s.
    Checks: internet, AvNav (:8080), Gemini proxy (:3001),
            AI Bridge (:3002), Signal K (:8099), Ollama (LAN 192.168.1.36:11434).
    """
    avnav_ok, avnav_charts = check_avnav()
    return jsonify({
        'internet':     check_internet(),
        'avnav':        avnav_ok,                     # AvNav's own status API
        'avnav_charts': avnav_charts,                 # surfaces blank charts (OB-O05)
        'gemini':       check_service(GEMINI_PORT),   # localhost:3001
        'ai_bridge':    check_service('3002'),        # localhost:3002 (Phase 5)
        'signalk':      check_service(SIGNALK_PORT),  # localhost:8099
        'ollama':       check_ollama(),               # 192.168.1.36:11434
        'gps':          check_gps(),                  # real position + 10s freshness
        'ais':          check_ais(),                  # receiving|no_targets|no_data
    })


@app.route('/health/report')
def health_report():
    """
    Full health report — written by AA5 HealthAgent every 24h.
    Returns score, issues list, and per-check details.
    """
    path = Path('/opt/d3kos/data/health-report.json')
    if path.exists():
        try:
            return jsonify(json.loads(path.read_text()))
        except Exception:
            pass
    return jsonify({'score': None, 'status': 'unknown', 'issues': [],
                    'updated': 'never'})


@app.route('/update/status')
def update_status():
    """
    Update notice — read by the Pi dashboard notice bar.
    Written by AA2 UpdateAgent when a new version is detected.
    Returns {'available': false} when no update pending.
    """
    path = Path('/opt/d3kos/data/update-notice.json')
    if path.exists():
        try:
            return jsonify(json.loads(path.read_text()))
        except Exception:
            pass
    return jsonify({'available': False})


@app.route('/agents/status')
def agents_status():
    """
    Agent health — read by the Pi dashboard status dot and engine-monitor page.
    Written by d3kos-agents.service every 5 minutes.
    Returns 'unknown' overall status if agent service is not running.
    """
    path = Path('/opt/d3kos/data/agents/agent_status.json')
    if path.exists():
        try:
            return jsonify(json.loads(path.read_text()))
        except Exception:
            pass
    return jsonify({'overall': 'unknown', 'updated': 'never', 'agents': {}})


@app.route('/settings')
def settings():
    """Settings & Help page — placeholder. Full build in Phase 4."""
    try:
        sys.path.insert(0, '/opt/d3kos/services/tier')
        from tier_service import _parse_tier
        lic = json.loads(Path('/opt/d3kos/config/license.json').read_text())
        tier_num = _parse_tier(lic.get('tier', 0))
    except Exception:
        tier_num = 0
    try:
        device_token = json.loads(
            Path('/opt/d3kos/config/device-token.json').read_text()
        ).get('device_token', '')
    except Exception:
        device_token = ''
    return render_template(
        'settings.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        signalk_port=SIGNALK_PORT,
        vessel_name=VESSEL_NAME,
        home_port=HOME_PORT_VAL,
        tier_num=tier_num,
        device_token=device_token,
    )


_APIKEYS_JSON = Path('/opt/d3kos/config/api-keys.json')
_TOKEN_FILE   = Path('/opt/d3kos/config/device-token.json')
_AMBOAT_REG_ENDPOINT = 'https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/generate-reg-token.php'


@app.route('/api/generate-reg-token', methods=['POST'])
def generate_reg_token():
    """
    Request a one-time registration code from HostPapa.
    The Pi authenticates with its AMBOAT_API_KEY + device_token.
    Returns: {token, register_url, expires_at, expires_min} or {error}.
    Called by the 'Register at AtMyBoat.com' button in settings.html.
    """
    try:
        keys         = json.loads(_APIKEYS_JSON.read_text())
        api_key      = keys.get('amboat_api_key', '')
        device_token = json.loads(_TOKEN_FILE.read_text()).get('device_token', '')
    except Exception as e:
        return jsonify({'error': f'Could not load Pi credentials: {e}'}), 500

    if not api_key or not device_token:
        return jsonify({'error': 'Pi credentials not configured. Complete Initial Setup first.'}), 500

    try:
        resp = requests.post(
            _AMBOAT_REG_ENDPOINT,
            json={'pi_id': device_token},
            headers={
                'Authorization':  f'Bearer {api_key}',
                'X-Device-Token': device_token,
                'Content-Type':   'application/json',
                'User-Agent':     'd3kOS/0.9.9.4 (Pi registration client)',
            },
            timeout=10,
        )
        data = resp.json()
    except requests.exceptions.Timeout:
        return jsonify({'error': 'AtMyBoat.com did not respond. Check your internet connection.'}), 504
    except Exception as e:
        return jsonify({'error': f'Request failed: {e}'}), 502

    if resp.status_code != 200 or not data.get('success'):
        msg = data.get('error', 'Unknown error from AtMyBoat.com')
        return jsonify({'error': msg}), resp.status_code

    return jsonify({'success': True, 'data': data.get('data', {})})


_BOATLOG_DB = Path('/opt/d3kos/data/boatlog/boatlog.db')


@app.route('/api/boatlog/entries')
def api_boatlog_entries():
    """
    BUG-24 — Return all boatlog entries from SQLite so boat-log.html can render
    them without the page having been open during the session.

    Read-only connection (uri=True, mode=ro) — the dashboard must never write
    to the log. Returns 200 with empty list when DB absent (kiosk with no log yet).
    Served on :3000 (same origin as boat-log.html) — sidesteps F3 loopback bind
    on boatlog-export-api.py :8095.
    """
    if not _BOATLOG_DB.exists():
        return jsonify({'ok': True, 'entries': []})
    try:
        uri = f'file:{_BOATLOG_DB}?mode=ro'
        with sqlite3.connect(uri, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT entry_id, timestamp, entry_type, content, "
                "latitude, longitude, weather_conditions "
                "FROM boatlog_entries ORDER BY timestamp DESC"
            ).fetchall()
        entries = [dict(r) for r in rows]
        return jsonify({'ok': True, 'entries': entries})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 500


_BOATLOG_API_BASE = 'http://127.0.0.1:8095'


@app.route('/api/boatlog/status')
def api_boatlog_status():
    """BUG-82 Option B — proxy to boatlog-export-api.py :8095 (loopback only) so remote browsers work."""
    try:
        r = requests.get(f'{_BOATLOG_API_BASE}/api/boatlog/status', timeout=5)
        return (r.content, r.status_code, {'Content-Type': r.headers.get('Content-Type', 'application/json')})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc), 'entry_count': 0}), 503


@app.route('/api/boatlog/voice-note', methods=['POST'])
def api_boatlog_voice_note():
    """BUG-82 Option B — proxy voice-note upload to :8095."""
    try:
        r = requests.post(
            f'{_BOATLOG_API_BASE}/api/boatlog/voice-note',
            data=request.get_data(),
            headers={k: v for k, v in request.headers if k.lower() not in ('host', 'content-length')},
            timeout=30
        )
        return (r.content, r.status_code, {'Content-Type': r.headers.get('Content-Type', 'application/json')})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 503


@app.route('/api/boatlog/export', methods=['POST'])
def api_boatlog_export():
    """BUG-82 Option B — proxy CSV export to :8095."""
    try:
        r = requests.post(f'{_BOATLOG_API_BASE}/api/boatlog/export', timeout=30)
        headers = {
            'Content-Type': r.headers.get('Content-Type', 'text/csv'),
            'Content-Disposition': r.headers.get('Content-Disposition', 'attachment; filename="boatlog.csv"'),
        }
        return (r.content, r.status_code, headers)
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 503


@app.route('/api/recovery-key')
def api_recovery_key():
    """
    FI4 — Return device_token for PWA Recovery Key display.
    Local-only endpoint — no auth needed (Pi LAN, port 3000).
    """
    try:
        device_token = json.loads(
            Path('/opt/d3kos/config/device-token.json').read_text()
        ).get('device_token', '')
    except Exception:
        device_token = ''
    if not device_token:
        return jsonify({'success': False, 'error': 'device-token.json not found'}), 404
    return jsonify({'success': True, 'device_token': device_token})


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


@app.route('/api/settings/vessel', methods=['POST'])
def api_settings_vessel():
    """
    Save vessel name and home port from the settings page.
    Body: {"vessel_name": "...", "home_port": "..."}
    Writes to vessel.env, preserving any other existing keys.
    """
    global VESSEL_NAME, HOME_PORT_VAL
    data = request.get_json(silent=True) or {}
    vessel_name = data.get('vessel_name', '').strip()
    home_port   = data.get('home_port', '').strip()
    if not vessel_name:
        return jsonify({'ok': False, 'error': 'Vessel name is required'}), 400

    # Preserve existing keys (e.g. ONBOARDING_RUNS, UI_LANG, EQUIPMENT_NOTES)
    existing = {}
    if os.path.exists(_VESSEL_ENV_PATH):
        with open(_VESSEL_ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    existing[k] = v
    existing['VESSEL_NAME'] = vessel_name
    existing['HOME_PORT']   = home_port

    os.makedirs(_cfg_dir, exist_ok=True)
    with open(_VESSEL_ENV_PATH, 'w') as f:
        for k, v in existing.items():
            f.write(f'{k}={v}\n')

    load_dotenv(_VESSEL_ENV_PATH, override=True)
    VESSEL_NAME   = os.getenv('VESSEL_NAME', vessel_name)
    HOME_PORT_VAL = os.getenv('HOME_PORT',   home_port)
    return jsonify({'ok': True})


@app.route('/api/vessel-home')
def vessel_home():
    """
    Return home port coordinates for weather.html GPS fallback.
    Reads HOME_PORT_LAT / HOME_PORT_LON from vessel.env.
    Returns {"lat": float, "lon": float, "home_port": str} if set,
    or {"lat": null, "lon": null, "home_port": str} if not configured.
    """
    try:
        lat = float(HOME_PORT_LAT) if HOME_PORT_LAT else None
        lon = float(HOME_PORT_LON) if HOME_PORT_LON else None
    except ValueError:
        lat = lon = None
    return jsonify({'lat': lat, 'lon': lon, 'home_port': HOME_PORT_VAL})


@app.route('/offline')
def offline():
    return render_template('offline.html')


# ── INC-02: New page routes (Session A stubs → replaced in Sessions B/C/D) ──

@app.route('/marine-vision')
def marine_vision():
    return render_template('marine-vision.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/boat-log')
def boat_log():
    return render_template('boat-log.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/upload-documents')
def upload_documents():
    return render_template('upload-documents.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/manage-documents')
def manage_documents():
    return render_template('manage-documents.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/ai-navigation')
def ai_navigation():
    return render_template('ai-navigation.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/engine-monitor')
def engine_monitor():
    return render_template('engine-monitor.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/helm-assistant')
def helm_assistant():
    return render_template('helm-assistant.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/anchor-watch')
def anchor_watch_page():
    return render_template('anchor-watch.html', vessel_name=VESSEL_NAME, ui_lang=UI_LANG)


@app.route('/manual')
def manual():
    """Serve the d3kOS user manual as a full HTML page."""
    return render_template('manual.html')


@app.route('/docs/<name>')
def serve_doc(name):
    """Serve a markdown doc file from /opt/d3kos/docs/ as plain text."""
    import re
    # Sanitise: allow only uppercase letters, underscores, digits
    if not re.fullmatch(r'[A-Z0-9_]+', name):
        return ('Not found', 404)
    doc_path = f'/opt/d3kos/docs/{name}.md'
    if not os.path.exists(doc_path):
        return ('Not found', 404)
    with open(doc_path, 'r') as f:
        return (f.read(), 200, {'Content-Type': 'text/plain; charset=utf-8'})


@app.route('/config/tier')
def config_tier():
    """Tier for M14 engine diagnostic gate. T0/T1 blocked, T2/T3 allowed."""
    try:
        sys.path.insert(0, '/opt/d3kos/services/tier')
        from tier_service import _parse_tier
        lic = json.loads(Path('/opt/d3kos/config/license.json').read_text())
        n = _parse_tier(lic.get('tier', 0))
        return jsonify({'tier': n, 'tier_str': 'T' + str(n)})
    except Exception:
        return jsonify({'tier': 0, 'tier_str': 'T0'})

@app.route('/anchor/set', methods=['POST'])
def anchor_set():
    """Get current vessel position from SK, tell ai_bridge to set anchor."""
    try:
        data = request.get_json(silent=True) or {}
        radius_m = float(data.get('radius_m', 25.0))
        r = requests.get('http://localhost:8099/signalk/v1/api/vessels/self/navigation/position', timeout=3)
        pos = r.json().get('value', {})
        lat = float(pos['latitude'])
        lon = float(pos['longitude'])
        result = requests.post('http://localhost:3002/anchor/set',
                               json={'lat': lat, 'lon': lon, 'radius_m': radius_m},
                               timeout=5)
        return jsonify(result.json())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/anchor/state')
def anchor_state():
    try:
        r = requests.get('http://localhost:3002/anchor/state', timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/anchor/dismiss', methods=['POST'])
def anchor_dismiss_proxy():
    try:
        r = requests.post('http://localhost:3002/anchor/dismiss', timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/anchor/clear', methods=['POST'])
def anchor_clear_proxy():
    try:
        r = requests.post('http://localhost:3002/anchor/clear', timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/anchor/advice')
def anchor_advice_proxy():
    try:
        r = requests.get('http://localhost:3002/anchor/advice', timeout=60)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/helm/mute', methods=['POST'])
def helm_mute_proxy():
    """Proxy HELM mute toggle to ai_bridge (same origin via Flask:3000 avoids CORS)."""
    try:
        r = requests.post('http://localhost:3002/helm/mute',
                          json=request.get_json(), timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
