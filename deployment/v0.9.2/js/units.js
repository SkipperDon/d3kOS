/**
 * d3kOS Units Conversion Utility
 * Version: 0.9.2
 * All data stored in imperial. This module converts for display only.
 * Storage rule: temperature=°F, pressure=PSI, speed=knots, depth=ft,
 *               fuel=gal, length=ft, weight=lb, displacement=ci
 */

const Units = {

  getPreference() {
    return localStorage.getItem('d3kos-measurement-system') || 'imperial';
  },

  setPreference(system) {
    if (system !== 'imperial' && system !== 'metric') {
      throw new Error('Invalid system: must be "imperial" or "metric"');
    }
    localStorage.setItem('d3kos-measurement-system', system);
    window.dispatchEvent(new CustomEvent('measurementSystemChanged', { detail: { system } }));
    fetch('/api/preferences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ measurement_system: system })
    }).catch(err => console.error('Preference sync failed:', err));
  },

  temperature: {
    toDisplay(fahrenheit) {
      if (typeof fahrenheit !== 'number' || isNaN(fahrenheit)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(((fahrenheit - 32) * 5 / 9) * 10) / 10) + '\u00b0C';
      }
      return (Math.round(fahrenheit * 10) / 10) + '\u00b0F';
    },
    toC(f) { return Math.round(((f - 32) * 5 / 9) * 10) / 10; },
    toF(c) { return Math.round(((c * 9 / 5) + 32) * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? '\u00b0C' : '\u00b0F'; }
  },

  pressure: {
    toDisplay(psi) {
      if (typeof psi !== 'number' || isNaN(psi)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(psi * 0.0689476 * 100) / 100) + ' bar';
      }
      return (Math.round(psi * 10) / 10) + ' PSI';
    },
    toBar(psi) { return Math.round(psi * 0.0689476 * 100) / 100; },
    toPSI(bar) { return Math.round(bar * 14.5038 * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? 'bar' : 'PSI'; }
  },

  speed: {
    toDisplay(knots) {
      if (typeof knots !== 'number' || isNaN(knots)) return 'N/A';
      const kts = Math.round(knots * 10) / 10;
      if (Units.getPreference() === 'metric') {
        const kmh = Math.round(knots * 1.852 * 10) / 10;
        return kts + ' kts (' + kmh + ' km/h)';
      }
      const mph = Math.round(knots * 1.15078 * 10) / 10;
      return kts + ' kts (' + mph + ' mph)';
    },
    toKmh(knots) { return Math.round(knots * 1.852 * 10) / 10; },
    toMph(knots) { return Math.round(knots * 1.15078 * 10) / 10; }
  },

  distance: {
    toDisplay(nm) {
      if (typeof nm !== 'number' || isNaN(nm)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(nm * 1.852 * 10) / 10) + ' km';
      }
      return (Math.round(nm * 10) / 10) + ' nm';
    },
    toKm(nm) { return Math.round(nm * 1.852 * 10) / 10; },
    toNm(km) { return Math.round((km / 1.852) * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? 'km' : 'nm'; }
  },

  depth: {
    toDisplay(feet) {
      if (typeof feet !== 'number' || isNaN(feet)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(feet * 0.3048 * 10) / 10) + ' m';
      }
      return (Math.round(feet * 10) / 10) + ' ft';
    },
    toMeters(ft) { return Math.round(ft * 0.3048 * 10) / 10; },
    toFeet(m) { return Math.round(m * 3.28084 * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? 'm' : 'ft'; }
  },

  fuel: {
    toDisplay(gallons) {
      if (typeof gallons !== 'number' || isNaN(gallons)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(gallons * 3.78541 * 10) / 10) + ' L';
      }
      return (Math.round(gallons * 10) / 10) + ' gal';
    },
    toLiters(gal) { return Math.round(gal * 3.78541 * 10) / 10; },
    toGallons(l) { return Math.round((l / 3.78541) * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? 'L' : 'gal'; }
  },

  length: {
    toDisplay(feet) {
      if (typeof feet !== 'number' || isNaN(feet)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(feet * 0.3048 * 10) / 10) + ' m';
      }
      return (Math.round(feet * 10) / 10) + ' ft';
    },
    toMeters(ft) { return Math.round(ft * 0.3048 * 10) / 10; },
    toFeet(m) { return Math.round(m * 3.28084 * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? 'm' : 'ft'; }
  },

  weight: {
    toDisplay(pounds) {
      if (typeof pounds !== 'number' || isNaN(pounds)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(pounds * 0.453592 * 10) / 10) + ' kg';
      }
      return (Math.round(pounds * 10) / 10) + ' lb';
    },
    toKg(lb) { return Math.round(lb * 0.453592 * 10) / 10; },
    toLb(kg) { return Math.round(kg * 2.20462 * 10) / 10; },
    unit() { return Units.getPreference() === 'metric' ? 'kg' : 'lb'; }
  },

  displacement: {
    toDisplay(ci) {
      if (typeof ci !== 'number' || isNaN(ci)) return 'N/A';
      if (Units.getPreference() === 'metric') {
        return (Math.round(ci * 0.0163871 * 10) / 10) + ' L';
      }
      return Math.round(ci) + ' ci';
    },
    toLiters(ci) { return Math.round(ci * 0.0163871 * 10) / 10; },
    toCi(l) { return Math.round(l / 0.0163871); },
    unit() { return Units.getPreference() === 'metric' ? 'L' : 'ci'; }
  }
};

// Load preference from backend on page load — sync localStorage with server.
// Only updates localStorage if the API value differs, then fires the change event
// so all gauges/displays re-render with the correct units.
(function loadPreferenceFromBackend() {
  fetch('/api/preferences')
    .then(r => r.json())
    .then(data => {
      const system = data.measurement_system || 'imperial';
      if (system === 'imperial' || system === 'metric') {
        const current = localStorage.getItem('d3kos-measurement-system');
        if (system !== current) {
          localStorage.setItem('d3kos-measurement-system', system);
          window.dispatchEvent(new CustomEvent('measurementSystemChanged', { detail: { system } }));
        }
      }
    })
    .catch(() => {}); // silently fall back to existing localStorage or 'imperial' default
})();

// CommonJS export for Node.js test environment
if (typeof module !== 'undefined' && module.exports) { module.exports = Units; }
