#!/usr/bin/env python3
"""
d3kOS Network Management API
Provides endpoints for WiFi/hotspot switching and network status
Port: 8101
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
HOTSPOT_SSID = "d3kOS"
HOTSPOT_CONNECTION = "d3kos"
WIFI_INTERFACE = "wlan0"

def run_command(cmd, timeout=10):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timeout',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def get_active_connection():
    """Get currently active network connection"""
    result = run_command("nmcli -t -f NAME,TYPE,DEVICE connection show --active")

    if not result['success']:
        return None

    lines = result['stdout'].split('\n')
    for line in lines:
        if not line:
            continue
        parts = line.split(':')
        if len(parts) >= 3:
            name, conn_type, device = parts[0], parts[1], parts[2]
            if device == WIFI_INTERFACE:
                return {
                    'name': name,
                    'type': conn_type,
                    'device': device
                }

    return None

def get_connection_details(connection_name):
    """Get detailed info about a connection"""
    result = run_command(f"nmcli -t -f GENERAL,IP4 connection show '{connection_name}'")

    if not result['success']:
        return {}

    details = {}
    lines = result['stdout'].split('\n')

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            details[key] = value

    return details

def get_wifi_signal_strength():
    """Get WiFi signal strength for active connection"""
    result = run_command("nmcli -t -f IN-USE,SIGNAL,SSID dev wifi list")

    if not result['success']:
        return 0

    lines = result['stdout'].split('\n')
    for line in lines:
        if line.startswith('*'):
            parts = line.split(':')
            if len(parts) >= 2:
                try:
                    return int(parts[1])
                except ValueError:
                    return 0

    return 0

def get_hotspot_clients():
    """Get list of devices connected to hotspot"""
    # Check if hotspot is active
    active_conn = get_active_connection()
    if not active_conn or active_conn['name'] != HOTSPOT_CONNECTION:
        return []

    # Get DHCP leases from dnsmasq
    leases_file = "/var/lib/NetworkManager/dnsmasq-wlan0.leases"

    if not os.path.exists(leases_file):
        # Try alternative location
        leases_file = "/var/lib/misc/dnsmasq.leases"

    if not os.path.exists(leases_file):
        return []

    clients = []
    try:
        with open(leases_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    # Format: timestamp mac ip hostname client-id
                    clients.append({
                        'mac': parts[1],
                        'ip': parts[2],
                        'hostname': parts[3] if parts[3] != '*' else 'Unknown',
                        'connected_at': datetime.fromtimestamp(int(parts[0])).isoformat()
                    })
    except Exception as e:
        print(f"Error reading DHCP leases: {e}", file=sys.stderr)

    return clients

@app.route('/status', methods=['GET'])
def get_status():
    """Get current network status"""
    active_conn = get_active_connection()

    if not active_conn:
        return jsonify({
            'connected': False,
            'mode': 'none',
            'message': 'No active connection'
        })

    is_hotspot = (active_conn['name'] == HOTSPOT_CONNECTION)

    status = {
        'connected': True,
        'mode': 'hotspot' if is_hotspot else 'client',
        'connection_name': active_conn['name'],
        'device': active_conn['device']
    }

    if is_hotspot:
        # Hotspot mode
        status['hotspot'] = {
            'ssid': HOTSPOT_SSID,
            'password': 'd3kos-2026',
            'clients': get_hotspot_clients(),
            'client_count': len(get_hotspot_clients())
        }
    else:
        # WiFi client mode
        details = get_connection_details(active_conn['name'])
        signal = get_wifi_signal_strength()

        # Extract SSID from connection details
        ssid = details.get('802-11-wireless.ssid', active_conn['name'])

        # Extract IP address
        ip_address = details.get('IP4.ADDRESS[1]', 'N/A')
        if ip_address and '/' in ip_address:
            ip_address = ip_address.split('/')[0]

        status['wifi'] = {
            'ssid': ssid,
            'signal': signal,
            'ip_address': ip_address,
            'gateway': details.get('IP4.GATEWAY', 'N/A')
        }

    return jsonify(status)

@app.route('/wifi/scan', methods=['GET'])
def scan_wifi():
    """Scan for available WiFi networks"""
    # Request fresh scan
    run_command(f"nmcli dev wifi rescan ifname {WIFI_INTERFACE}")

    # Wait a moment for scan to complete
    time.sleep(2)

    # Get scan results
    result = run_command(f"nmcli -t -f SSID,SIGNAL,SECURITY dev wifi list ifname {WIFI_INTERFACE}")

    if not result['success']:
        return jsonify({
            'success': False,
            'networks': [],
            'error': result['stderr']
        })

    networks = []
    seen_ssids = set()

    lines = result['stdout'].split('\n')
    for line in lines:
        if not line:
            continue

        parts = line.split(':')
        if len(parts) >= 3:
            ssid = parts[0]

            # Skip hidden networks and duplicates
            if not ssid or ssid in seen_ssids:
                continue

            seen_ssids.add(ssid)

            try:
                signal = int(parts[1])
            except ValueError:
                signal = 0

            security = parts[2] if len(parts) > 2 else ''

            networks.append({
                'ssid': ssid,
                'signal': signal,
                'security': security,
                'secured': bool(security and security != '--')
            })

    # Sort by signal strength
    networks.sort(key=lambda x: x['signal'], reverse=True)

    return jsonify({
        'success': True,
        'networks': networks,
        'count': len(networks)
    })

@app.route('/wifi/connect', methods=['POST'])
def connect_wifi():
    """Connect to a WiFi network"""
    data = request.get_json()

    if not data or 'ssid' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing SSID'
        }), 400

    ssid = data['ssid']
    password = data.get('password', '')

    # First, deactivate hotspot if active
    active_conn = get_active_connection()
    if active_conn and active_conn['name'] == HOTSPOT_CONNECTION:
        run_command(f"nmcli connection down '{HOTSPOT_CONNECTION}'")
        time.sleep(2)

    # Try to connect
    if password:
        # Connect with password
        cmd = f"nmcli dev wifi connect '{ssid}' password '{password}' ifname {WIFI_INTERFACE}"
    else:
        # Connect without password (open network)
        cmd = f"nmcli dev wifi connect '{ssid}' ifname {WIFI_INTERFACE}"

    result = run_command(cmd, timeout=30)

    if result['success']:
        return jsonify({
            'success': True,
            'message': f'Connected to {ssid}',
            'ssid': ssid
        })
    else:
        return jsonify({
            'success': False,
            'error': result['stderr'] or 'Connection failed',
            'details': result['stdout']
        }), 400

@app.route('/hotspot/enable', methods=['POST'])
def enable_hotspot():
    """Activate hotspot mode"""
    # Deactivate current connection
    active_conn = get_active_connection()
    if active_conn and active_conn['name'] != HOTSPOT_CONNECTION:
        run_command(f"nmcli connection down '{active_conn['name']}'")
        time.sleep(2)

    # Activate hotspot
    result = run_command(f"nmcli connection up '{HOTSPOT_CONNECTION}'", timeout=30)

    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Hotspot enabled',
            'ssid': HOTSPOT_SSID,
            'password': 'd3kos-2026'
        })
    else:
        return jsonify({
            'success': False,
            'error': result['stderr'] or 'Failed to enable hotspot',
            'details': result['stdout']
        }), 400

@app.route('/hotspot/disable', methods=['POST'])
def disable_hotspot():
    """Deactivate hotspot mode"""
    active_conn = get_active_connection()

    if not active_conn or active_conn['name'] != HOTSPOT_CONNECTION:
        return jsonify({
            'success': False,
            'error': 'Hotspot is not active'
        }), 400

    result = run_command(f"nmcli connection down '{HOTSPOT_CONNECTION}'")

    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Hotspot disabled'
        })
    else:
        return jsonify({
            'success': False,
            'error': result['stderr'] or 'Failed to disable hotspot'
        }), 400

@app.route('/hotspot/clients', methods=['GET'])
def list_hotspot_clients():
    """Get list of connected hotspot clients"""
    clients = get_hotspot_clients()

    return jsonify({
        'success': True,
        'clients': clients,
        'count': len(clients)
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'd3kos-network-api',
        'timestamp': datetime.now().isoformat()
    })

# ── Language / i18n API ───────────────────────────────────────────────────
I18N_DIR        = '/opt/d3kos/config/i18n'
ONBOARDING_PATH = '/opt/d3kos/config/onboarding.json'
SUPPORTED_LANGUAGES = [
    'en','fr','it','es','el','hr','tr','de','nl',
    'sv','no','da','fi','pt','ar','zh','ja','uk'
]

def _load_onboarding():
    try:
        with open(ONBOARDING_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_onboarding(cfg):
    tmp = ONBOARDING_PATH + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ONBOARDING_PATH)

@app.route('/api/language', methods=['GET'])
def get_language():
    cfg = _load_onboarding()
    return jsonify({'language': cfg.get('language', 'en'), 'dir': cfg.get('dir', 'ltr')})

@app.route('/api/language', methods=['POST'])
def set_language():
    data = request.get_json(silent=True) or {}
    lang = data.get('language', 'en')
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': f'Unsupported language: {lang}'}), 400
    direction = 'rtl' if lang == 'ar' else 'ltr'
    cfg = _load_onboarding()
    cfg['language'] = lang
    cfg['dir'] = direction
    _save_onboarding(cfg)
    return jsonify({'status': 'ok', 'language': lang, 'dir': direction})

@app.route('/api/i18n/<lang_code>', methods=['GET'])
def get_translation(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return jsonify({'error': f'Unsupported language: {lang_code}'}), 404
    filepath = os.path.join(I18N_DIR, f'{lang_code}.json')
    if not os.path.exists(filepath):
        filepath = os.path.join(I18N_DIR, 'en.json')
        if not os.path.exists(filepath):
            return jsonify({'error': 'Translation file not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=3600'
    return response

@app.route('/api/languages', methods=['GET'])
def list_languages():
    available = [c for c in SUPPORTED_LANGUAGES
                 if os.path.exists(os.path.join(I18N_DIR, f'{c}.json'))]
    return jsonify({'languages': available, 'total': len(available)})


ONBOARDING_FILE = '/opt/d3kos/config/onboarding.json'


@app.route('/network/check-default-password', methods=['GET'])
def check_default_password():
    """Returns {default: true} if password has not been changed yet."""
    try:
        with open(ONBOARDING_FILE, 'r') as f:
            data = json.load(f)
        if data.get('password_changed'):
            return jsonify({'default': False})
    except Exception:
        pass
    return jsonify({'default': True})


@app.route('/network/change-password', methods=['POST'])
def change_password():
    """Change the d3kos system password. Requires sudoers entry for chpasswd."""
    data = request.get_json(silent=True) or {}
    new_password = data.get('new_password', '').strip()

    if not new_password or len(new_password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
    if new_password == 'pi':
        return jsonify({'success': False, 'error': 'Cannot use default password'}), 400

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
            with open(ONBOARDING_FILE, 'r') as f:
                onboarding = json.load(f)
        except Exception:
            onboarding = {}
        onboarding['password_changed'] = True
        with open(ONBOARDING_FILE, 'w') as f:
            json.dump(onboarding, f, indent=2)

        return jsonify({'success': True})
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout changing password'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print(f"Starting d3kOS Network API on port 8101...")
    app.run(host='127.0.0.1', port=8101, debug=False)
