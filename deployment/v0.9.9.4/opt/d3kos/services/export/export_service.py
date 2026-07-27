#!/usr/bin/env python3
"""
d3kOS Export Service
Saves exports to /home/d3kos/d3kos-exports/ for Tier 1 sync
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

EXPORT_BASE = "/home/d3kos/d3kos-exports"

class ExportHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/export/boatlog":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode("utf-8"))
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"boatlog_{timestamp}.json"
                filepath = os.path.join(EXPORT_BASE, "boatlogs", filename)
                
                # Save to file
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)
                
                # Response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {"success": True, "filename": filename, "path": filepath}
                self.wfile.write(json.dumps(response).encode())
                
                print(f"✓ Exported boatlog to {filepath}")
                
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
                print(f"✗ Export failed: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    PORT = 8090
    server = HTTPServer(("localhost", PORT), ExportHandler)
    print(f"d3kOS Export Service running on port {PORT}")
    print(f"Export directory: {EXPORT_BASE}")
    server.serve_forever()
