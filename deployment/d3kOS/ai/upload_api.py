#!/usr/bin/env python3
"""
d3kOS File Upload API v2
Handles manual PDF uploads (Python 3.13 compatible)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import subprocess
import json
from pathlib import Path

UPLOAD_DIR = "/opt/d3kos/data/manuals"
DOCUMENT_PROCESSOR = "/opt/d3kos/services/ai/document_processor.py"
PROCESS_LOG = "/opt/d3kos/logs/document_processor.log"

class UploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload/manual':
            self.handle_upload()
        elif self.path == '/upload/status':
            self.handle_status()
        else:
            self.send_error(404)

    def handle_status(self):
        """Return last N lines of document processor log"""
        try:
            if os.path.exists(PROCESS_LOG):
                with open(PROCESS_LOG, 'r') as f:
                    lines = f.readlines()
                tail = ''.join(lines[-50:])
            else:
                tail = "No processing log found yet."
            self.send_json_response({'log': tail})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_upload(self):
        try:
            # Get content type and boundary
            content_type = self.headers.get('Content-Type', '')
            if not 'multipart/form-data' in content_type:
                self.send_json_response({'error': 'Content-Type must be multipart/form-data'}, 400)
                return

            # Extract boundary
            boundary = None
            for part in content_type.split(';'):
                if 'boundary=' in part:
                    boundary = part.split('=')[1].strip()
                    break

            if not boundary:
                self.send_json_response({'error': 'No boundary in Content-Type'}, 400)
                return

            # Read body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # Parse multipart data
            boundary_bytes = f"--{boundary}".encode()
            parts = body.split(boundary_bytes)

            filename = None
            file_data = None
            manual_type = 'boat'

            for part in parts:
                if b'Content-Disposition' in part:
                    # Extract filename
                    if b'filename=' in part:
                        # Split headers from content
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            headers = part[:header_end].decode('utf-8', errors='ignore')
                            content = part[header_end+4:]

                            # Remove trailing boundary markers
                            if content.endswith(b'\r\n'):
                                content = content[:-2]

                            # Extract filename from headers
                            for line in headers.split('\n'):
                                if 'filename=' in line:
                                    fn_start = line.find('filename="') + 10
                                    fn_end = line.find('"', fn_start)
                                    if fn_end > fn_start:
                                        filename = line[fn_start:fn_end]
                                    break

                            if filename:
                                file_data = content

                    # Extract type field
                    elif b'name="type"' in part:
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            content = part[header_end+4:].decode('utf-8', errors='ignore').strip()
                            if content:
                                manual_type = content

            if not filename or not file_data:
                self.send_json_response({'error': 'No file uploaded or filename missing'}, 400)
                return

            # Validate PDF
            if not filename.lower().endswith('.pdf'):
                self.send_json_response({'error': 'Only PDF files are allowed'}, 400)
                return

            # Sanitize filename
            filename = self.sanitize_filename(filename)
            filepath = os.path.join(UPLOAD_DIR, filename)

            # Create upload directory
            Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
            Path(PROCESS_LOG).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(filepath, 'wb') as f:
                f.write(file_data)

            # Launch document processor in background — non-blocking.
            # Scanned PDFs require tesseract OCR which can take 30+ minutes.
            # We return success immediately; indexing continues in the background.
            log_file = open(PROCESS_LOG, 'a')
            log_file.write(f"\n{'='*60}\n")
            log_file.write(f"Processing: {filename}  type={manual_type}\n")
            log_file.write(f"{'='*60}\n")
            log_file.flush()

            subprocess.Popen(
                ['python3', DOCUMENT_PROCESSOR, filepath, manual_type],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                close_fds=True
            )
            # Note: log_file stays open for the child process; OS closes it when child exits.

            self.send_json_response({
                'success': True,
                'filename': filename,
                'size': len(file_data),
                'message': 'Manual uploaded. Indexing running in background — check /upload/status for progress.'
            })

        except Exception as e:
            import traceback
            self.send_json_response({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, 500)

    def sanitize_filename(self, filename):
        """Sanitize filename to prevent path traversal"""
        filename = os.path.basename(filename)
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        return filename

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
        pass


def main():
    port = 8081
    server = HTTPServer(('0.0.0.0', port), UploadHandler)
    print(f"Upload API server running on port {port}")
    server.serve_forever()


if __name__ == '__main__':
    main()
