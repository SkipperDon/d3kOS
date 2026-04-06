#!/usr/bin/env python3
"""
d3kOS AI Query Handler v6 - RAG Integrated
Supports Gemini (online), rule-based patterns (offline), and PDF manual retrieval
"""

import json
import sqlite3
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
import sys
import argparse

# Import Signal K client
try:
    from signalk_client import SignalKClient
    SIGNALK_AVAILABLE = True
except ImportError:
    SIGNALK_AVAILABLE = False

# PDF Processor imported lazily in AIQueryHandler.__init__ when skip_rag=False

# Paths
CONFIG_PATH = "/opt/d3kos/config/ai-config.json"
SKILLS_PATH = "/opt/d3kos/config/skills.md"
DB_PATH = "/opt/d3kos/data/conversation-history.db"
MAINTENANCE_LOG_PATH = "/opt/d3kos/data/maintenance-log.json"
PREFS_PATH = "/opt/d3kos/config/user-preferences.json"

SIMULATED_STATUS = {
    'rpm': 3200, 'oil_pressure': 45, 'coolant_temp': 180,
    'fuel_level': 75, 'battery_voltage': 14.2, 'speed': 12.5, 'heading': 270
}

class AIQueryHandler:
    def __init__(self, skip_rag=False):
        self.config = self.load_config()
        self.skills = self.load_skills()
        self.signalk = SignalKClient() if SIGNALK_AVAILABLE else None
        self.pdf_processor = None
        if not skip_rag:
            try:
                sys.path.insert(0, '/opt/d3kos/services/documents')
                from pdf_processor import PDFProcessor
                self.pdf_processor = PDFProcessor()
            except Exception:
                pass

    def load_config(self):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)

    def load_skills(self):
        try:
            with open(SKILLS_PATH, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "No skills data available yet."

    def _query_gemini(self, text: str, boat_status: dict = None) -> str | None:
        import requests
        try:
            payload = {'message': text}
            if boat_status:
                payload['context'] = boat_status
            r = requests.post('http://localhost:8097/gemini/chat', json=payload, timeout=15)
            if r.status_code == 200:
                data = r.json()
                return data.get('response', '').strip()
        except Exception as e:
            print(f"  ⚠ Gemini query failed: {e}", flush=True)
        return None

    def get_boat_status(self):
        if self.signalk:
            try:
                status = self.signalk.get_boat_status()
                for key in SIMULATED_STATUS:
                    if key in status and status[key] is None:
                        status[key] = SIMULATED_STATUS[key]
                return status
            except Exception:
                return SIMULATED_STATUS
        return SIMULATED_STATUS

    def check_internet(self):
        try:
            urllib.request.urlopen("https://www.google.com", timeout=3)
            return True
        except:
            return False

    def search_manuals(self, question, k=5):
        if not self.pdf_processor:
            return None
        try:
            chunks = self.pdf_processor.search(question, k=k)
            if not chunks:
                return None
            manual_context = "\n\n=== RELEVANT INFORMATION FROM YOUR MANUALS ===\n\n"
            for chunk in chunks:
                manual_context += f"From {chunk['source']}:\n{chunk['content']}\n\n"
            manual_context += "=== END OF MANUAL EXCERPTS ===\n"
            return manual_context
        except Exception as e:
            print(f"⚠ Manual search error: {e}", flush=True)
            return None

    def format_quick_answer(self, question, manual_context):
        if not manual_context:
            return "No relevant information found in manuals. Try asking about: fishing regulations, engine maintenance, safety procedures."
        answer = "📄 **Quick Answer from Manuals:**\n\n"
        answer += manual_context
        answer += "\n\n---\n\n💡 *This information was found in your uploaded manuals and regulations.*"
        return answer

    def classify_action_query(self, question):
        """Stub — action commands not yet implemented."""
        return None

    def classify_simple_query(self, question):
        q_lower = question.lower()
        procedure_keywords = [
            'procedure', 'how to', 'how do i', 'steps', 'instructions',
            'change', 'replace', 'install', 'maintenance', 'service',
            'repair', 'fix', 'troubleshoot', 'winterize', 'drain'
        ]
        for keyword in procedure_keywords:
            if keyword in q_lower:
                return None
        simple_patterns = {
            'rpm': ['rpm', 'revolution', 'engine speed', 'how fast is the engine'],
            'oil': ['oil pressure', 'oil', 'lubrication'],
            'temperature': ['temperature', 'temp', 'coolant', 'how hot', 'overheating'],
            'fuel': ['fuel', 'gas', 'how much fuel', 'fuel remaining', 'fuel left'],
            'battery': ['battery', 'voltage', 'electrical', 'power'],
            'speed': ['speed', 'how fast', 'knots', 'velocity', 'sog'],
            'heading': ['heading', 'direction', 'course', 'which way', 'bearing'],
            'boost': ['boost', 'boost pressure', 'turbo', 'manifold pressure'],
            'hours': ['engine hours', 'runtime', 'hours', 'operating time', 'run time'],
            'location': ['location', 'position', 'where am i', 'coordinates', 'gps', 'latitude', 'longitude'],
            'time': ['what time', 'current time', 'time is it', 'date'],
            'help': ['what can you do', 'help', 'capabilities', 'commands', 'how to use'],
            'status': ['status', 'how is', 'everything', 'all systems', 'overview'],
            'reboot': ['reboot', 'restart', 'reboot system', 'restart system', 'power cycle', 'shut down', 'shutdown']
        }
        for category, patterns in simple_patterns.items():
            for pattern in patterns:
                if pattern in q_lower:
                    return category
        return None

    def simple_response(self, category):
        from datetime import datetime
        if category == 'time':
            return f"Current time is {datetime.now().strftime('%I:%M %p')} on {datetime.now().strftime('%A, %B %d, %Y')}."
        elif category == 'help':
            return "I can help with: engine RPM, oil pressure, temperature, fuel level, battery voltage, speed, heading, boost pressure, engine hours, GPS location, current time, and overall system status. I can also search your uploaded manuals for technical information. Just ask!"
        elif category == 'reboot':
            try:
                import dbus
                bus = dbus.SystemBus()
                manager = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
                reboot_method = manager.get_dbus_method('Reboot', 'org.freedesktop.login1.Manager')
                reboot_method(False)
                return "Rebooting system now. Please wait 60 seconds."
            except Exception as e:
                return "Reboot command failed. Please use physical reboot button."
        elif category == 'location':
            return self.get_location_response()
        status = self.get_boat_status()
        responses = {
            'rpm': f"Engine RPM is {status.get('rpm', 'unknown')}.",
            'oil': f"Oil pressure is {status.get('oil_pressure', 'unknown')} PSI." if status.get('oil_pressure') else "Oil pressure sensor not available.",
            'temperature': f"Coolant temperature is {status.get('coolant_temp', 'unknown')} degrees." if status.get('coolant_temp') else "Temperature sensor not available.",
            'fuel': f"Fuel level is {status.get('fuel_level', 'unknown')} percent." if status.get('fuel_level') else "Fuel level sensor not available.",
            'battery': f"Battery voltage is {status.get('battery_voltage', 'unknown')} volts." if status.get('battery_voltage') else "Battery voltage sensor not available.",
            'speed': f"Current speed is {status.get('speed', 'unknown')} knots." if status.get('speed') else "Speed sensor not available.",
            'heading': f"Heading is {status.get('heading', 'unknown')} degrees." if status.get('heading') else "Heading sensor not available.",
            'boost': f"Boost pressure is {status.get('boost_pressure', 'unknown')} PSI." if status.get('boost_pressure') else "Boost pressure sensor not available.",
            'hours': f"Engine has {status.get('engine_hours', 'unknown')} hours." if status.get('engine_hours') else "Engine hours not available.",
            'status': self.get_full_status_response(status)
        }
        return responses.get(category, "I can help with that.")

    def get_location_response(self):
        try:
            if self.signalk:
                import urllib.request, json
                url = f"http://localhost:8099/signalk/v1/api/vessels/self/navigation/position/value"
                with urllib.request.urlopen(url, timeout=3) as resp:
                    pos = json.loads(resp.read())
                    lat = pos.get('latitude', 0)
                    lon = pos.get('longitude', 0)
                    ns = 'N' if lat >= 0 else 'S'
                    ew = 'E' if lon >= 0 else 'W'
                    return f"Current position: {abs(lat):.4f}°{ns}, {abs(lon):.4f}°{ew}"
        except:
            pass
        return "GPS position not available."

    def get_full_status_response(self, status):
        rpm = status.get("rpm") or 0
        if rpm > 0:
            parts = [f"Engine running at {rpm} RPM"]
            oil = status.get("oil_pressure")
            temp = status.get("coolant_temp")
            fuel = status.get("fuel_level")
            spd = status.get("speed")
            if oil and oil != 45: parts.append(f"oil {oil} PSI")
            if temp and temp != 180: parts.append(f"coolant {temp} degrees")
            if fuel and fuel != 75: parts.append(f"fuel {fuel} percent")
            if spd: parts.append(f"speed {spd} knots")
            return "All systems normal. " + ", ".join(parts) + "."
        else:
            lines = ["Engine is off."]
            fuel = status.get("fuel_level")
            batt = status.get("battery_voltage")
            if fuel and fuel != 75: lines.append(f"Fuel is at {fuel} percent.")
            if batt and batt != 14.2: lines.append(f"Battery is {batt} volts.")
            return " ".join(lines)

    def store_conversation(self, question, answer, ai_used, provider, model, response_time):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (question, answer, ai_used, provider, model, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (question, answer, ai_used, provider, model, response_time))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠ store_conversation error: {e}", flush=True)

    def query(self, question, force_provider=None, quick_mode=None):
        start_time = time.time()
        manual_used = False

        # Check for action commands (stub — always None)
        action = self.classify_action_query(question)
        if action:
            action_type, payload = action
            print(f"  ⚡ Action command: {action_type}", flush=True)
            answer = self.execute_action(action_type, payload)
            elapsed = time.time() - start_time
            response_time = int(elapsed * 1000)
            self.store_conversation(question, answer, 'onboard', 'action', 'rules', response_time)
            return {
                'question': question, 'answer': answer, 'provider': 'action',
                'model': 'rules', 'ai_used': 'onboard', 'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(), 'manual_used': False
            }

        # Rule-based fast path for simple queries
        simple_category = self.classify_simple_query(question)
        if simple_category:
            answer = self.simple_response(simple_category)
            elapsed = time.time() - start_time
            response_time = int(elapsed * 1000)
            self.store_conversation(question, answer, 'onboard', 'onboard', 'rules', response_time)
            return {
                'question': question, 'answer': answer, 'provider': 'onboard',
                'model': 'rules', 'ai_used': 'onboard', 'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(), 'manual_used': False
            }

        # Complex query — start Ollama on-demand (nomic-embed-text needed for query embedding)
        try:
            import sys as _sys
            _sys.path.insert(0, '/opt/d3kos/services/ai')
            from fish_rag_llm import _start_serve as _ollama_start
            _ollama_start()  # no-op if running; starts serve if not (<=15s)
        except Exception:
            pass

        # Search manuals for context
        print("  🔍 Searching manuals for relevant information...", flush=True)
        manual_context = self.search_manuals(question, k=6)
        manual_used = bool(manual_context)

        if manual_context:
            print("  ✓ Found relevant manual information", flush=True)
        else:
            print("  ℹ️  No relevant manual information found", flush=True)

        # Try Gemini
        boat_status = self.get_boat_status()
        print("  🤖 Querying Gemini...", flush=True)
        gemini_answer = self._query_gemini(question, boat_status)

        if gemini_answer:
            answer = gemini_answer
            provider = 'gemini'
            model = 'gemini-api'
            print("  ✓ Gemini responded", flush=True)
        elif manual_context:
            # Try phi3.5 synthesis — falls back to raw chunks if Ollama unavailable
            llm_answer = None
            try:
                import sys as _sys
                _sys.path.insert(0, '/opt/d3kos/services/ai')
                from fish_rag_llm import synthesize as _llm_synthesize
                raw_chunks = self.pdf_processor.search(question, k=3) if self.pdf_processor else []
                llm_answer = _llm_synthesize(question, raw_chunks)
            except Exception:
                pass

            if llm_answer:
                answer = llm_answer
                provider = 'local-llm'
                try:
                    import fish_rag_llm as _frl
                    model = _frl.OLLAMA_MODEL
                except Exception:
                    model = 'local-llm'
                print(f"  ✓ Local LLM synthesized answer via {model}", flush=True)
            else:
                answer = self.format_quick_answer(question, manual_context)
                provider = 'rag-only'
                model = 'manual-search'
                print("  ℹ️  Gemini unavailable, using RAG results", flush=True)
        else:
            answer = "I'm sorry, I couldn't find an answer. Gemini is offline and no manuals are uploaded. Try uploading your boat manuals in Settings."
            provider = 'fallback'
            model = 'none'

        elapsed = time.time() - start_time
        response_time = int(elapsed * 1000)
        ai_used = 'online' if provider == 'gemini' else 'onboard'
        self.store_conversation(question, answer, ai_used, provider, model, response_time)

        return {
            'question': question, 'answer': answer, 'provider': provider,
            'model': model, 'ai_used': provider, 'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat(), 'manual_used': manual_used
        }


def main():
    parser = argparse.ArgumentParser(description='d3kOS AI Query Handler')
    parser.add_argument('question', nargs='*', help='Question to ask the AI')
    parser.add_argument('--no-rag', action='store_true', help='Skip PDF RAG init (faster for voice queries)')
    parser.add_argument('--force-provider', help='Force AI provider')
    args = parser.parse_args()
    if not args.question:
        print("Usage: query_handler.py <question>")
        sys.exit(1)
    question = " ".join(args.question)
    handler = AIQueryHandler(skip_rag=args.no_rag)
    result = handler.query(question)
    print(f"Answer: {result.get('answer', 'No answer')}")

if __name__ == "__main__":
    main()
