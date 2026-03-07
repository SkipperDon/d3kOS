# community-api.py
# community API Flask service port 8095

from flask import Flask,jsonify,request
import requests,json,os
from anonymiser import strip_position

app = Flask(__name__)

COMMUNITY_PREFS_PATH = '/opt/d3kos/config/community-prefs.json'

def load_community_prefs():
    try:
        with open(COMMUNITY_PREFS_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def is_hazard_reporting_enabled():
    prefs = load_community_prefs()
    return prefs.get('hazard_reporting', False)

@app.route('/api/community/marker', methods=['POST'])
def post_marker():
    if not is_hazard_reporting_enabled():
        return jsonify({'error': 'Hazard reporting not enabled'}), 503
    
    try:
        data = request.get_json(force=True)
        category = data.get('category')
        description = data.get('description')
        lat = data.get('lat')
        lon = data.get('lon')
        
        if not all([category, description, lat, lon]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Anonymise position
        pos = strip_position(lat, lon)

        payload = {
            'category': category,
            'description': description,
            'lat': pos['lat_approx'],
            'lon': pos['lon_approx']
        }
        
        response = requests.post(
            'https://atmyboat.com/api/community/markers',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({'ok': True})
        else:
            return jsonify({'error': f'Failed to post marker: {response.text}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/markers', methods=['GET'])
def get_markers():
    if not is_hazard_reporting_enabled():
        return jsonify({'error': 'Hazard reporting not enabled'}), 503
    
    bbox = request.args.get('bbox')
    if not bbox:
        return jsonify({'error': 'Missing bbox parameter'}), 400
    
    try:
        response = requests.get(
            f'https://atmyboat.com/api/community/markers?bbox={bbox}',
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Failed to fetch markers: {response.text}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

VALID_PREFS = {'benchmark_sharing', 'boat_map', 'hazard_reporting', 'knowledge_base'}

@app.route('/api/community/prefs', methods=['GET'])
def get_prefs():
    return jsonify(load_community_prefs())

@app.route('/api/community/prefs', methods=['POST'])
def set_pref():
    data = request.get_json(force=True)
    key = data.get('key')
    value = data.get('value')
    if key not in VALID_PREFS or not isinstance(value, bool):
        return jsonify({'error': 'Invalid key or value'}), 400
    prefs = load_community_prefs()
    prefs[key] = value
    with open(COMMUNITY_PREFS_PATH, 'w') as f:
        json.dump(prefs, f)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8103, debug=False)
