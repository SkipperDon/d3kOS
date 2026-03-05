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
MAINTENANCE_LOG_PATH = "/opt/d3kos/data/maintenance-log.json"
PREFS_PATH = "/opt/d3kos/config/user-preferences.json"

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

    def search_manuals(self, question, k=6):
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
            rag_results = self.pdf_processor.search(question, k=k)

            if not rag_results:
                return None

            # Filter weak results by distance
            MAX_DISTANCE = 0.40
            results = [r for r in rag_results if r.get('distance', 1.0) < MAX_DISTANCE]
            if not results:
                # No strong matches — fall through to Gemini
                return self._query_gemini(question)

            # Build context with source info
            context_parts = []
            for r in results:
                source = r.get('metadata', {}).get('source', 'unknown')
                context_parts.append(f"[Source: {source}]\n{r['document']}")
            rag_context = '\n\n'.join(context_parts)

            # Format the results
            manual_context = "\n\n=== RELEVANT INFORMATION FROM YOUR MANUALS ===\n\n"

            for i, chunk in enumerate(results, 1):
                manual_context += f"From {chunk['metadata']['source']}:\n"
                manual_context += chunk['document'] + "\n\n"

            return manual_context

        except Exception as e:
            print(f"⚠ Manual search failed: {e}", flush=True)
            return None