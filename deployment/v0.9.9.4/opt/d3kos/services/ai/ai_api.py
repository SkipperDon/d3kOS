#!/usr/bin/env python3
"""
d3kOS AI API Server
Simple HTTP API for web interface with persistent handler (for Signal K caching)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os

# Add query handler to path
sys.path.insert(0, '/opt/d3kos/services/ai')
from query_handler import AIQueryHandler

# Create handler once at module level (persistent cache across requests)
print("Initializing AI query handler...", flush=True)
query_handler = AIQueryHandler()
print("AI query handler ready (Signal K cache enabled)", flush=True)

class AIAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/ai/query':
            self.handle_ai_query()
        else:
            self.send_error(404)
    
    def handle_ai_query(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            question = data.get('question', '')
            provider = data.get('provider')
            quick_mode = data.get('quick_mode', False)
            
            if not question:
                self.send_json_response({'error': 'Question is required'}, 400)
                return
            
            # Query AI handler (reuse global instance for persistent caching)
            result = query_handler.query(question, force_provider=provider, quick_mode=quick_mode)
            
            # Send response
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    port = 8089
    server = HTTPServer(('0.0.0.0', port), AIAPIHandler)
    print(f"AI API server running on port {port}", flush=True)
    print("Signal K cache TTL: 3.0 seconds", flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()
