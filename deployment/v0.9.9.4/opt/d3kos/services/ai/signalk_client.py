#!/usr/bin/env python3
"""
d3kOS Signal K Client with Caching
Fetches real-time boat data from Signal K server with configurable cache
"""

import json
import urllib.request
import urllib.error
import time

SIGNALK_URL = "http://localhost:8099/signalk/v1/api/"

class SignalKClient:
    def __init__(self, base_url=SIGNALK_URL, cache_ttl=3.0):
        """
        Initialize Signal K client with caching
        
        Args:
            base_url: Signal K API base URL
            cache_ttl: Cache time-to-live in seconds (default: 3.0 seconds)
                      Set to 0 to disable caching
        """
        self.base_url = base_url
        self.cache_ttl = cache_ttl
        self._cache = None
        self._cache_timestamp = 0
        
    def _is_cache_valid(self):
        """Check if cached data is still valid"""
        if self.cache_ttl == 0:
            return False
        if self._cache is None:
            return False
        age = time.time() - self._cache_timestamp
        return age < self.cache_ttl
    
    def get_value(self, path, default=None):
        """Get a single value from Signal K"""
        try:
            url = f"{self.base_url}vessels/self/{path}"
            response = urllib.request.urlopen(url, timeout=2)
            data = json.loads(response.read().decode('utf-8'))
            
            if 'value' in data:
                return data['value']
            return default
        except:
            return default
    
    def _dig(self, obj, *path):
        """Safely navigate nested dict and return value."""
        for k in path:
            if not isinstance(obj, dict) or k not in obj:
                return None
            obj = obj[k]
        if isinstance(obj, dict):
            return obj.get('value')
        return obj

    def get_boat_status(self, force_refresh=False):
        """Fetch all boat data in a single SK request for speed."""
        if not force_refresh and self._is_cache_valid():
            return self._cache.copy()

        status = {}
        try:
            url = f"{self.base_url}vessels/self"
            resp = urllib.request.urlopen(url, timeout=3)
            d = json.loads(resp.read())

            # Engine RPM
            rpm_hz = self._dig(d, 'propulsion', 'port', 'revolutions')
            status['rpm'] = int(rpm_hz * 60) if rpm_hz else 0

            # Oil pressure (Pa -> PSI)
            oil_pa = self._dig(d, 'propulsion', 'port', 'oilPressure')
            status['oil_pressure'] = round(oil_pa * 0.000145038, 1) if oil_pa else None

            # Coolant temp (K -> F)
            temp_k = self._dig(d, 'propulsion', 'port', 'temperature')
            status['coolant_temp'] = round((temp_k - 273.15) * 9/5 + 32, 1) if temp_k else None

            # Fuel level (ratio -> %)
            fuel = self._dig(d, 'tanks', 'fuel', '0', 'currentLevel')
            status['fuel_level'] = round(fuel * 100, 1) if fuel is not None else None

            # Battery voltage
            batt = self._dig(d, 'electrical', 'batteries', '0', 'voltage')
            status['battery_voltage'] = round(batt, 1) if batt else None

            # Speed over ground (m/s -> knots) — 0 is valid (stationary)
            sog = self._dig(d, 'navigation', 'speedOverGround')
            status['speed'] = round(sog * 1.94384, 1) if sog is not None else None

            # Course over ground (rad -> deg) — 0 is valid (due North)
            cog = self._dig(d, 'navigation', 'courseOverGroundTrue')
            status['heading'] = round(cog * 180 / 3.14159, 0) if cog is not None else None

            # Engine hours (s -> h)
            hours = self._dig(d, 'propulsion', 'port', 'runTime')
            status['engine_hours'] = round(hours / 3600, 1) if hours else None

        except Exception:
            pass  # Will use SIMULATED_STATUS fallback in caller

        self._cache = status
        self._cache_timestamp = time.time()
        return status.copy()
    
    def clear_cache(self):
        """Manually clear the cache"""
        self._cache = None
        self._cache_timestamp = 0

def main():
    """Test Signal K client with caching"""
    client = SignalKClient(cache_ttl=3.0)
    
    print("Fetching boat status (first call - will fetch from Signal K)...")
    start = time.time()
    status1 = client.get_boat_status()
    time1 = time.time() - start
    print(f"Time: {time1:.3f}s")
    print(json.dumps(status1, indent=2))
    
    print("\nFetching boat status again (should use cache)...")
    start = time.time()
    status2 = client.get_boat_status()
    time2 = time.time() - start
    print(f"Time: {time2:.3f}s (cached: {time2 < 0.001})")
    print(json.dumps(status2, indent=2))
    
    print("\nWaiting 4 seconds for cache to expire...")
    time.sleep(4)
    
    print("\nFetching boat status after cache expiry (will fetch fresh)...")
    start = time.time()
    status3 = client.get_boat_status()
    time3 = time.time() - start
    print(f"Time: {time3:.3f}s")
    print(json.dumps(status3, indent=2))

if __name__ == "__main__":
    main()
