# anonymiser.py
# community PII anonymiser utility
import hashlib
import hmac
import json

def anon_token(boat_uuid):
    with open('/opt/d3kos/config/api-keys.json', 'r') as f:
        keys = json.load(f)
    device_api_key = keys.get('device_api_key', '')
    return hmac.new(device_api_key.encode(), boat_uuid.encode(), hashlib.sha256).hexdigest()

def strip_position(lat, lon, precision=2):
    return {
        'lat_approx': round(lat, precision),
        'lon_approx': round(lon, precision)
    }

def strip_vessel_name(data):
    for key in ['name', 'vessel_name', 'mmsi', 'callsign']:
        data.pop(key, None)
    return data
