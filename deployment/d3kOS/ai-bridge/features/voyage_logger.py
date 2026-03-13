"""
d3kOS AI Bridge — Feature 3: Voyage Log Summarization

Two trigger modes:
  Auto:      AvNav track recording status changes to 'stopped'
  On-demand: POST /summarize-voyage from dashboard

Privacy: only summary statistics are sent to AI — raw GPS coordinates are never transmitted.
"""

import os
import glob
import logging
import threading
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

from utils.avnav_client import get_nav_data, download_track_gpx, get_track_list
from utils.geo import gpx_total_distance_nm

log = logging.getLogger(__name__)

GEMINI_PROXY_URL = os.environ.get('GEMINI_PROXY_URL', 'http://localhost:3001')
VESSEL_NAME      = os.environ.get('VESSEL_NAME', 'the vessel')
HOME_PORT        = os.environ.get('HOME_PORT', 'home port')
LOG_DIR          = os.environ.get('LOG_DIR', '/home/d3kos/logs')

_VOYAGE_LOG_DIR = os.path.join(LOG_DIR, 'voyage-summaries')

_LOG_PROMPT = """\
You are a marine navigation assistant for vessel {vessel_name}, home port {home_port}.

Write a plain-English voyage log entry for the following passage:

Departure: approximately {start_lat:.3f}N, {start_lon:.3f}W at {start_time}
Arrival:   approximately {end_lat:.3f}N, {end_lon:.3f}W at {end_time}
Total distance: {total_nm:.1f} nautical miles
Elapsed time: {elapsed_hours:.1f} hours
Average speed: {avg_speed:.1f} knots
Track points recorded: {point_count}

Write a 3-5 sentence log entry as a skipper would write in a paper log:
- Mention departure and arrival locations by approximate name if recognizable
- Include distance, time, and average speed
- Write in past tense ("Departed..." or "We departed...")
- Keep it factual and nautical in tone
- Do not speculate about weather or conditions not provided"""

_GPX_NS = {'gpx': 'http://www.topografix.com/GPX/1/1'}


class VoyageLogger:
    """
    Monitors AvNav recording status and generates voyage summaries.
    broadcast_fn pushes SSE events to the dashboard.
    """

    def __init__(self, broadcast_fn):
        self._broadcast = broadcast_fn
        self._stop_event = threading.Event()
        self._thread = None
        self._last_recording_status = None

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name='voyage-logger'
        )
        self._thread.start()
        log.info('VoyageLogger started — monitoring AvNav recording status')

    def stop(self):
        self._stop_event.set()

    def summarize_latest(self) -> dict:
        """
        On-demand: summarize the most recent AvNav track.
        Returns {'ok': bool, 'summary': str, 'filename': str}.
        Called from /summarize-voyage endpoint.
        """
        tracks = get_track_list()
        if not tracks:
            return {'ok': False, 'error': 'No tracks available in AvNav.'}

        # Most recent track is usually first in the list
        latest = tracks[0]
        track_name = latest.get('name', '')
        if not track_name:
            return {'ok': False, 'error': 'Could not determine track filename.'}

        return self._summarize_track(track_name)

    def summarize_by_filename(self, filename: str) -> dict:
        """Summarize a specific GPX track by filename."""
        return self._summarize_track(filename)

    def _loop(self):
        import time
        while not self._stop_event.is_set():
            try:
                self._check_recording_stopped()
            except Exception as exc:
                log.error('VoyageLogger error: %s', exc)
            time.sleep(30)  # poll every 30s

    def _check_recording_stopped(self):
        nav = get_nav_data()
        status = nav.get('recording_status')

        if status is None:
            return

        # Detect transition from recording → stopped
        if (self._last_recording_status == 'recording' and
                status in ('stopped', 'paused', None)):
            log.info('AvNav track recording stopped — auto-generating voyage summary')
            t = threading.Thread(target=self._auto_summarize, daemon=True)
            t.start()

        self._last_recording_status = status

    def _auto_summarize(self):
        """Auto-trigger: summarize today's track when recording stops."""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        filename = f'{today}.gpx'
        result = self._summarize_track(filename)
        if result.get('ok'):
            self._broadcast('voyage_summary', {
                'trigger': 'auto',
                'summary': result['summary'],
                'filename': result.get('filename', filename),
                'source': result.get('source', 'unknown'),
            })

    def _summarize_track(self, filename: str) -> dict:
        gpx_text = download_track_gpx(filename)
        if not gpx_text:
            return {'ok': False, 'error': f'Could not download track: {filename}'}

        summary = parse_gpx_summary(gpx_text)
        if not summary:
            return {'ok': False, 'error': 'Track file empty or unparseable.'}

        elapsed_s = summary.get('elapsed_seconds', 0)
        elapsed_h = elapsed_s / 3600.0 if elapsed_s else 0.0
        avg_speed = (summary['total_nm'] / elapsed_h) if elapsed_h > 0 else 0.0

        prompt = _LOG_PROMPT.format(
            vessel_name   = VESSEL_NAME,
            home_port     = HOME_PORT,
            start_lat     = abs(summary['start_lat']),
            start_lon     = abs(summary['start_lon']),
            end_lat       = abs(summary['end_lat']),
            end_lon       = abs(summary['end_lon']),
            start_time    = summary.get('start_time', 'unknown'),
            end_time      = summary.get('end_time', 'unknown'),
            total_nm      = summary['total_nm'],
            elapsed_hours = elapsed_h,
            avg_speed     = avg_speed,
            point_count   = summary['point_count'],
        )

        ai_result = _call_ai(prompt)
        text   = ai_result.get('response', '')
        source = ai_result.get('source', 'error')

        if not text:
            return {'ok': False, 'error': 'AI returned empty response.'}

        saved_path = _save_summary(text, filename)
        return {
            'ok':       True,
            'summary':  text,
            'filename': saved_path,
            'source':   source,
        }

    def list_recent_summaries(self, count: int = 5) -> list:
        """Return the most recent N voyage summaries as list of dicts."""
        files = sorted(
            glob.glob(os.path.join(_VOYAGE_LOG_DIR, '*_voyage_summary.txt')),
            reverse=True,
        )[:count]

        result = []
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    result.append({
                        'filename': os.path.basename(f),
                        'text':     fh.read(),
                    })
            except Exception:
                pass
        return result


def parse_gpx_summary(gpx_text: str) -> dict | None:
    """
    Extract statistics from GPX text without exposing raw GPS data.
    Returns summary dict or None if parsing fails.
    """
    try:
        root = ET.fromstring(gpx_text)
    except ET.ParseError as exc:
        log.warning('GPX parse error: %s', exc)
        return None

    points = root.findall('.//gpx:trkpt', _GPX_NS)
    if not points:
        # Try without namespace
        points = root.findall('.//trkpt')
    if not points:
        return None

    first = points[0]
    last  = points[-1]

    # Coordinates
    try:
        start_lat = float(first.get('lat'))
        start_lon = float(first.get('lon'))
        end_lat   = float(last.get('lat'))
        end_lon   = float(last.get('lon'))
    except (TypeError, ValueError):
        return None

    # Timestamps — must use 'is not None' check, not 'or':
    # ElementTree leaf elements (no child elements) evaluate as falsy.
    start_time_el = first.find('gpx:time', _GPX_NS)
    if start_time_el is None:
        start_time_el = first.find('time')
    end_time_el = last.find('gpx:time', _GPX_NS)
    if end_time_el is None:
        end_time_el = last.find('time')
    start_time = start_time_el.text if start_time_el is not None else None
    end_time   = end_time_el.text   if end_time_el   is not None else None

    # Elapsed time
    elapsed_seconds = None
    if start_time and end_time:
        try:
            fmt = '%Y-%m-%dT%H:%M:%SZ'
            t1  = datetime.strptime(start_time, fmt)
            t2  = datetime.strptime(end_time,   fmt)
            elapsed_seconds = (t2 - t1).total_seconds()
        except ValueError:
            pass

    # Total distance (privacy: only summary stat sent to AI)
    coord_list = []
    for pt in points:
        try:
            coord_list.append((float(pt.get('lat')), float(pt.get('lon'))))
        except (TypeError, ValueError):
            pass

    total_nm = gpx_total_distance_nm(coord_list)

    return {
        'start_lat':       start_lat,
        'start_lon':       start_lon,
        'end_lat':         end_lat,
        'end_lon':         end_lon,
        'start_time':      start_time or 'unknown',
        'end_time':        end_time   or 'unknown',
        'elapsed_seconds': elapsed_seconds,
        'point_count':     len(points),
        'total_nm':        total_nm,
    }


def _save_summary(text: str, source_filename: str) -> str:
    """Save summary text to LOG_DIR/voyage-summaries/ and return saved path."""
    os.makedirs(_VOYAGE_LOG_DIR, exist_ok=True)
    ts       = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M')
    basename = f'{ts}_voyage_summary.txt'
    path     = os.path.join(_VOYAGE_LOG_DIR, basename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'# Voyage Summary — {ts}\n')
        f.write(f'# Source track: {source_filename}\n\n')
        f.write(text)
    log.info('Voyage summary saved: %s', path)
    return path


def _call_ai(prompt: str) -> dict:
    try:
        resp = requests.post(
            f'{GEMINI_PROXY_URL}/ask',
            json={'prompt': prompt},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.warning('AI proxy call failed: %s', exc)
        return {'response': '', 'source': 'error'}
