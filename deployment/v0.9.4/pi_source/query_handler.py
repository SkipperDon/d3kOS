#!/usr/bin/env python3
"""
d3kOS AI Query Handler v6 - RAG Integrated
Supports OpenRouter (online), rule-based patterns (offline), and PDF manual retrieval
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
    print("⚠ Signal K client not available, using simulated data")

# Import PDF Processor for RAG
sys.path.insert(0, '/opt/d3kos/services/documents')
try:
    from pdf_processor import PDFProcessor
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠ PDF Processor not available, manual search disabled")

# Paths
CONFIG_PATH = "/opt/d3kos/config/ai-config.json"
SKILLS_PATH = "/opt/d3kos/config/skills.md"
DB_PATH = "/opt/d3kos/data/conversation-history.db"

# Fallback simulated boat status (used if Signal K unavailable)
SIMULATED_STATUS = {
    'rpm': 3200,
    'oil_pressure': 45,
    'coolant_temp': 180,
    'fuel_level': 75,
    'battery_voltage': 14.2,
    'speed': 12.5,
    'heading': 270
}

class AIQueryHandler:
    def __init__(self):
        self.config = self.load_config()
        self.skills = self.load_skills()
        self.signalk = SignalKClient() if SIGNALK_AVAILABLE else None

        # Initialize PDF processor for RAG
        if RAG_AVAILABLE:
            try:
                print("Initializing PDF RAG system...", flush=True)
                self.pdf_processor = PDFProcessor()
                print("✓ PDF RAG system ready", flush=True)
            except Exception as e:
                print(f"⚠ PDF RAG initialization failed: {e}", flush=True)
                self.pdf_processor = None
        else:
            self.pdf_processor = None

    def load_config(self):
        """Load AI configuration"""
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)

    def load_skills(self):
        """Load skills.md context"""
        try:
            with open(SKILLS_PATH, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "No skills data available yet."

    def _query_gemini(self, text: str, boat_status: dict = None) -> str | None:
        """Query Gemini API proxy. Returns response text or None on failure."""
        import requests
        try:
            payload = {'message': text}
            if boat_status:
                payload['context'] = boat_status
            r = requests.post(
                'http://localhost:8097/gemini/chat',
                json=payload,
                timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                return data.get('response', '').strip()
        except Exception as e:
            print(f"  ⚠ Gemini query failed: {e}", flush=True)
        return None

    def get_boat_status(self):
        """Get current boat status from Signal K or simulated data"""
        if self.signalk:
            try:
                status = self.signalk.get_boat_status()
                # Replace None values with simulated fallback
                for key in SIMULATED_STATUS:
                    if key in status and status[key] is None:
                        status[key] = SIMULATED_STATUS[key]
                return status
            except Exception as e:
                print(f"⚠ Signal K error: {e}, using simulated data")
                return SIMULATED_STATUS
        return SIMULATED_STATUS

    def check_internet(self):
        """Check if internet is available"""
        try:
            urllib.request.urlopen("https://www.google.com", timeout=3)
            return True
        except:
            return False

    def search_manuals(self, question, k=5):
        """
        Search PDF manuals for relevant information

        Args:
            question: User's question
            k: Number of relevant chunks to retrieve

        Returns:
            String with relevant manual passages or None
        """
        if not self.pdf_processor:
            return None

        try:
            # Search the RAG database
            chunks = self.pdf_processor.search(question, k=k)

            if not chunks:
                return None

            # Format the results
            manual_context = "\n\n=== RELEVANT INFORMATION FROM YOUR MANUALS ===\n\n"

            for i, chunk in enumerate(chunks, 1):
                manual_context += f"From {chunk['source']}:\n"
                manual_context += f"{chunk['content']}\n\n"

            manual_context += "=== END OF MANUAL EXCERPTS ===\n"

            return manual_context

        except Exception as e:
            print(f"⚠ Manual search error: {e}", flush=True)
            return None
    def format_quick_answer(self, question, manual_context):
        """Format RAG search results as a quick answer (no LLM processing)"""
        if not manual_context:
            return "No relevant information found in manuals. Try asking about: fishing regulations, engine maintenance, safety procedures."
        
        answer = "📄 **Quick Answer from Manuals:**\n\n"
        answer += manual_context
        answer += "\n\n---\n"
        answer += "\n💡 *This information was found in your uploaded manuals and regulations.*"
        return answer


    def query_openrouter(self, question, context, manual_context=None):
        """Query OpenRouter API with optional manual context"""
        config = self.config["providers"]["openrouter"]

        if not config["api_key"]:
            raise ValueError("OpenRouter API key not configured")

        # Use default_model from config
        model = config["default_model"]

        # Get current boat status for real-time data
        boat_status = self.get_boat_status()
        status_text = f"""
Current Boat Status (Real-time Sensor Data):
- Engine RPM: {boat_status.get('rpm', 'N/A')}
- Oil Pressure: {boat_status.get('oil_pressure', 'N/A')} PSI
- Coolant Temperature: {boat_status.get('coolant_temp', 'N/A')}°F
- Fuel Level: {boat_status.get('fuel_level', 'N/A')}%
- Battery Voltage: {boat_status.get('battery_voltage', 'N/A')}V
- Speed: {boat_status.get('speed', 'N/A')} knots
- Heading: {boat_status.get('heading', 'N/A')}°
- Boost Pressure: {boat_status.get('boost_pressure', 'N/A')} PSI
- Engine Hours: {boat_status.get('engine_hours', 'N/A')} hours
"""

        # Build system prompt with manual context if available
        system_prompt = f"""You are a marine assistant for d3kOS.

{status_text}

Context from boat knowledge base:
{context}
"""

        # Add manual context if found
        if manual_context:
            system_prompt += f"""
{manual_context}

IMPORTANT: The manual excerpts above contain specific information about this boat's systems.
When answering, prioritize information from the manuals over general knowledge.
Quote the manual when appropriate and cite the source document.
"""
        else:
            system_prompt += """
No specific manual information found for this question. Provide general marine guidance.
"""

        system_prompt += """
Provide concise, accurate answers based on this boat's specific configuration and current sensor readings."""

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"]
        }

        req = urllib.request.Request(
            config["api_endpoint"],
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://d3kos.atmyboat.com",
                "X-Title": "d3kOS Marine Assistant"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=config["timeout"]/1000) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result["choices"][0]["message"]["content"], model
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def classify_simple_query(self, question):
        """Check if this is a simple query that can be answered with rules"""
        q_lower = question.lower()

        # FIRST: Diagnostic intent — these questions need Gemini, not rule-based answers
        # "what causes white smoke at high speed" contains 'speed' but is NOT a speed query
        diagnostic_intents = [
            'why ', 'why is', 'why does', 'why am i',
            'what causes', 'what could cause', 'what would cause',
            'what is wrong', 'what might be wrong',
            'is it normal', 'should i be concerned', 'should i worry',
            'explain ', 'tell me about', 'what does it mean',
            'could it be', 'what happens when', 'what happens if',
            'white smoke', 'black smoke', 'blue smoke', 'grey smoke',
            'strange noise', 'weird noise', 'unusual noise', 'knocking', 'banging',
            'vibrat', 'shaking', 'rough idle',
            'overheating', 'running hot', 'too hot',
            'diagnos', 'what should i do', 'is this bad',
        ]
        for intent in diagnostic_intents:
            if intent in q_lower:
                return None  # Send to Gemini

        # SECOND: Procedure/how-to questions — send to RAG
        procedure_keywords = [
            'procedure', 'how to', 'what type', 'which', 'what kind', 'how do i', 'steps', 'instructions',
            'change', 'replace', 'install', 'maintenance', 'service',
            'repair', 'fix', 'troubleshoot', 'winterize', 'drain'
        ]
        for keyword in procedure_keywords:
            if keyword in q_lower:
                return None  # Force RAG search for procedures

        # THIRD: Simple status queries — tightened to avoid false positives
        simple_patterns = {
            'rpm': ['what is the rpm', 'current rpm', 'engine rpm', 'rpm is', 'rpm reading',
                    'revolution', 'how fast is the engine'],
            'oil': ['oil pressure', 'oil psi', 'lubrication pressure'],
            'temperature': ['coolant temperature', 'engine temperature', 'coolant temp', 'engine temp',
                            'how hot is the engine', 'how hot is the coolant', 'what is the temperature'],
            'fuel': ['fuel level', 'fuel remaining', 'fuel left', 'how much fuel', 'how much gas',
                     'fuel percentage', 'tank level'],
            'battery': ['battery level', 'battery voltage', 'battery charge', 'battery status',
                        'what is the voltage', 'current voltage', 'system voltage'],
            'speed': ['what is my speed', 'current speed', 'how fast am i', 'speed over ground',
                      'boat speed', 'sog', 'speed in knots', 'knots right now'],
            'heading': ['what is my heading', 'current heading', 'what direction am i', 'which way am i',
                        'bearing to', 'course over ground'],
            'boost': ['boost pressure', 'turbo pressure', 'manifold pressure', 'boost level'],
            'hours': ['engine hours', 'how many hours', 'operating hours', 'run time', 'runtime',
                      'how long has the engine'],
            'location': ['where am i', 'my location', 'my position', 'current position',
                         'coordinates', 'latitude', 'longitude', 'gps position'],
            'time': ['what time is it', 'current time', 'time is it', 'what is the date', 'current date'],
            'help': ['what can you do', 'help me', 'your capabilities', 'list commands', 'how to use you'],
            'status': ['system status', 'all systems', 'overall status', 'boat status', 'engine status',
                       'how is everything', 'status report', 'give me an overview'],
            'reboot': ['reboot', 'restart', 'power cycle', 'shut down', 'shutdown']
        }

        for category, patterns in simple_patterns.items():
            for pattern in patterns:
                if pattern in q_lower:
                    return category

        return None


    def _load_units_preference(self) -> str:
        """Returns 'imperial' or 'metric' from user-preferences.json"""
        try:
            import json as _json
            with open('/opt/d3kos/config/user-preferences.json') as f:
                return _json.load(f).get('measurement_system', 'imperial')
        except Exception:
            return 'imperial'

    def _format_temperature(self, fahrenheit: float, system: str) -> str:
        if system == 'metric':
            c = round((fahrenheit - 32) * 5 / 9, 1)
            return f"{c} degrees Celsius"
        return f"{round(fahrenheit, 1)} degrees Fahrenheit"

    def _format_pressure(self, psi: float, system: str) -> str:
        if system == 'metric':
            bar = round(psi * 0.0689476, 2)
            return f"{bar} bar"
        return f"{round(psi, 1)} PSI"

    def _format_speed(self, knots: float, system: str) -> str:
        if system == 'metric':
            kmh = round(knots * 1.852, 1)
            return f"{round(knots, 1)} knots, which is {kmh} kilometers per hour"
        mph = round(knots * 1.15078, 1)
        return f"{round(knots, 1)} knots, which is {mph} miles per hour"

    def simple_response(self, category):
        """Generate rule-based response for simple queries using current boat data"""
        from datetime import datetime

        # For queries that don't need boat status, return immediately
        if category == 'time':
            return f"Current time is {datetime.now().strftime('%I:%M %p')} on {datetime.now().strftime('%A, %B %d, %Y')}."
        elif category == 'help':
            return "I can help with: engine RPM, oil pressure, temperature, fuel level, battery voltage, speed, heading, boost pressure, engine hours, GPS location, current time, and overall system status. I can also search your uploaded manuals for technical information. Just ask!"
        elif category == 'reboot':
            # Emergency reboot command (for when touchscreen is broken)
            # Uses D-Bus to communicate with systemd-logind (industry standard)
            try:
                import dbus
                bus = dbus.SystemBus()
                manager = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
                reboot_method = manager.get_dbus_method('Reboot', 'org.freedesktop.login1.Manager')
                reboot_method(False)  # False = immediate, no confirmation
                return "Rebooting system now. Please wait 60 seconds."
            except Exception as e:
                import logging
                logging.error(f"D-Bus reboot failed: {e}")
                return "Reboot command failed. Please use physical reboot button."
        elif category == 'location':
            return self.get_location_response()

        # Get current boat status only when needed
        status = self.get_boat_status()

        _sys = self._load_units_preference()
        responses = {
            'rpm': f"Engine RPM is {status.get('rpm', 'unknown')}.",
            'oil': f"Oil pressure is {self._format_pressure(status['oil_pressure'], _sys)}." if status.get('oil_pressure') else "Oil pressure sensor not available.",
            'temperature': f"Coolant temperature is {self._format_temperature(status['coolant_temp'], _sys)}." if status.get('coolant_temp') else "Temperature sensor not available.",
            'fuel': f"Fuel level is {status.get('fuel_level', 'unknown')} percent." if status.get('fuel_level') else "Fuel level sensor not available.",
            'battery': f"Battery voltage is {status.get('battery_voltage', 'unknown')} volts." if status.get('battery_voltage') else "Battery voltage sensor not available.",
            'speed': f"Current speed is {self._format_speed(status['speed'], _sys)}." if status.get('speed') else "Speed sensor not available.",
            'heading': f"Heading is {status.get('heading', 'unknown')} degrees." if status.get('heading') else "Heading sensor not available.",
            'boost': f"Boost pressure is {self._format_pressure(status['boost_pressure'], _sys)}." if status.get('boost_pressure') else "Boost pressure sensor not available.",
            'hours': f"Engine has {status.get('engine_hours', 'unknown')} hours." if status.get('engine_hours') else "Engine hours not available.",
            'status': self.get_full_status_response(status)
        }
        return responses.get(category, "I can help with that.")

    def get_location_response(self):
        """Get GPS location response"""
        try:
            # Try to get position from Signal K
            if self.signalk:
                import urllib.request
                import json
                url = f"{self.signalk.base_url}vessels/self/navigation/position"
                response = urllib.request.urlopen(url, timeout=2)
                data = json.loads(response.read().decode('utf-8'))
                if 'value' in data:
                    lat = data['value'].get('latitude')
                    lon = data['value'].get('longitude')
                    if lat and lon:
                        lat_dir = "N" if lat >= 0 else "S"
                        lon_dir = "E" if lon >= 0 else "W"
                        return f"Current position is {abs(lat):.4f}° {lat_dir}, {abs(lon):.4f}° {lon_dir}."
        except:
            pass
        return "GPS position not available."

    def get_full_status_response(self, status):
        """Generate comprehensive status response"""
        parts = []

        if status.get('rpm') is not None and status.get('rpm') > 0:
            parts.append(f"Engine running at {status['rpm']} RPM")
        elif status.get('rpm') == 0:
            parts.append("Engine off")

        if status.get('oil_pressure'):
            parts.append(f"oil {status['oil_pressure']} PSI")

        if status.get('coolant_temp'):
            parts.append(f"temperature {status['coolant_temp']} degrees")

        if status.get('fuel_level'):
            parts.append(f"fuel {status['fuel_level']} percent")

        if parts:
            return "All systems normal. " + ", ".join(parts) + "."
        else:
            return "System status: sensors initializing or engine not running."

    def query_ollama(self, question, context, manual_context=None):
        """Query local Ollama API with optional manual context"""
        config = self.config["providers"]["ollama"]

        if not config.get("enabled", False):
            raise ValueError("Ollama provider not enabled")

        model = config["default_model"]

        # Get current boat status for real-time data
        boat_status = self.get_boat_status()
        status_text = f"""
Current Boat Status (Real-time Sensor Data):
- Engine RPM: {boat_status.get('rpm', 'N/A')}
- Oil Pressure: {boat_status.get('oil_pressure', 'N/A')} PSI
- Coolant Temperature: {boat_status.get('coolant_temp', 'N/A')}°F
- Fuel Level: {boat_status.get('fuel_level', 'N/A')}%
- Battery Voltage: {boat_status.get('battery_voltage', 'N/A')}V
- Speed: {boat_status.get('speed', 'N/A')} knots
- Heading: {boat_status.get('heading', 'N/A')}°
- Boost Pressure: {boat_status.get('boost_pressure', 'N/A')} PSI
- Engine Hours: {boat_status.get('engine_hours', 'N/A')} hours
"""

        # Build system prompt with manual context if available
        system_prompt = f"""You are a marine assistant for d3kOS.

{status_text}

Context from boat knowledge base:
{context}
"""

        # Add manual context if found
        if manual_context:
            system_prompt += f"""
{manual_context}

IMPORTANT: The manual excerpts above contain specific information about this boat's systems.
When answering, prioritize information from the manuals over general knowledge.
Quote the manual when appropriate and cite the source document.
"""
        else:
            system_prompt += """
No specific manual information found for this question. Provide general marine guidance.
"""

        system_prompt += """
Provide concise, accurate answers based on this boat's specific configuration and current sensor readings."""

        # Ollama API format
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "stream": False,
            "options": {
                "temperature": config["temperature"]
            }
        }

        req = urllib.request.Request(
            config["api_endpoint"],
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=config["timeout"]/1000) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result["message"]["content"], model
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def query_onboard(self, question, context):
        """Query onboard AI - uses rule-based responses for supported queries

        Phi-2 removed for performance. Complex queries require internet connection.
        Supported queries: rpm, oil, temperature, fuel, battery, speed, heading,
        boost, hours, location, time, help, status
        """

        # Check if this is a simple query
        simple_category = self.classify_simple_query(question)

        if simple_category:
            print("  ⚡ Using fast rule-based response with real boat data", flush=True)
            return self.simple_response(simple_category), "rules"

        # Complex query - requires internet
        print("  ℹ️  Complex query requires internet connection", flush=True)
        supported = "rpm, oil pressure, temperature, fuel, battery, speed, heading, boost, hours, location, time, help, status"
        return f"I can answer simple questions offline: {supported}. For complex questions, please connect to internet.", "rules"

    def query(self, question, force_provider=None, quick_mode=None):
        """
        Simplified query handler - RAG-only manual search
        
        Args:
            question: The user's question
            force_provider: Ignored (kept for API compatibility)
            quick_mode: Ignored (always uses RAG-only)
        
        Returns:
            dict with answer, provider, model, response_time, manual_used
        """
        start_time = time.time()
        manual_context = None
        manual_used = False
        
        # Check if simple query FIRST (rule-based patterns)
        simple_category = self.classify_simple_query(question)
        if simple_category:
            # Use rule-based response immediately (RPM, oil, temp, etc.)
            answer = self.simple_response(simple_category)
            elapsed = time.time() - start_time
            response_time = int(elapsed * 1000)
            
            # Store in database
            self.store_conversation(question, answer, 'onboard', 'onboard', 'rules', response_time)
            
            return {
                'question': question,
                'answer': answer,
                'provider': 'onboard',
                'model': 'rules',
                'ai_used': 'onboard',
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(),
                'manual_used': False
            }
        
        # Complex query - search manuals for context
        print("  🔍 Searching manuals for relevant information...", flush=True)
        manual_context = self.search_manuals(question, k=10)
        manual_used = bool(manual_context)

        if manual_context:
            print("  ✓ Found relevant manual information", flush=True)
        else:
            print("  ℹ️  No relevant manual information found", flush=True)

        # Try Gemini first (faster, smarter responses)
        boat_status = self.get_boat_status()
        print("  🤖 Querying Gemini...", flush=True)
        gemini_answer = self._query_gemini(question, boat_status)

        if gemini_answer:
            answer = gemini_answer
            provider = 'gemini'
            model = 'gemini-api'
            print("  ✓ Gemini responded", flush=True)
        else:
            # Fallback: show RAG results directly
            answer = self.format_quick_answer(question, manual_context)
            provider = 'rag-only'
            model = 'manual-search'
            print("  ℹ️  Gemini unavailable, using RAG results", flush=True)

        elapsed = time.time() - start_time
        response_time = int(elapsed * 1000)

        ai_used = 'online' if provider == 'gemini' else 'onboard'
        self.store_conversation(question, answer, ai_used, provider, model, response_time)

        return {
            'question': question,
            'answer': answer,
            'provider': provider,
            'model': model,
            'ai_used': provider,
            'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat(),
            'manual_used': manual_used
        }

    def store_conversation(self, question, answer, ai_used, provider, model, response_time):
        """Store conversation in database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conversations
            (question, answer, ai_used, provider, model, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (question, answer, ai_used, provider, model, response_time))

        conn.commit()
        conn.close()

def main():
    """Test the query handler"""
    parser = argparse.ArgumentParser(description='d3kOS AI Query Handler')
    parser.add_argument('question', nargs='*', help='Question to ask the AI')
    parser.add_argument('--force-provider', choices=['openrouter', 'onboard'],
                       help='Force specific AI provider')
    parser.add_argument('--classify-only', action='store_true',
                       help='Only classify query as simple or complex, do not answer')
    args = parser.parse_args()

    if not args.question:
        print("Usage: query_handler.py [--force-provider openrouter|onboard] [--classify-only] <question>")
        sys.exit(1)

    question = " ".join(args.question)

    handler = AIQueryHandler()

    # Classify-only mode (for intelligent routing in voice assistant)
    if args.classify_only:
        category = handler.classify_simple_query(question)
        if category:
            print(f"SIMPLE: {category}")
            sys.exit(0)
        else:
            print("COMPLEX")
            sys.exit(1)

    # Regular query mode
    print(f"Question: {question}")
    print("Processing...\n")

    result = handler.query(question, force_provider=args.force_provider)

    print(f"Provider: {result['provider']}")
    print(f"Model: {result['model']}")
    print(f"Manual Used: {result.get('manual_used', False)}")
    print(f"Response Time: {result['response_time_ms']}ms ({result['response_time_ms']/1000:.1f}s)")
    print(f"\nAnswer:\n{result['answer']}")

if __name__ == "__main__":
    main()
