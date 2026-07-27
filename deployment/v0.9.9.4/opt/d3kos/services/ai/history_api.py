#!/usr/bin/env python3
"""
d3kOS Conversation History API
Serves conversation history and manual management endpoints
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from pathlib import Path
import os
import sys

# Add PDF processor to path for RAG integration
sys.path.insert(0, '/opt/d3kos/services/documents')

DB_PATH = "/opt/d3kos/data/conversation-history.db"
MANUALS_DIR = "/opt/d3kos/data/manuals"
PORT = 8082

# Import PDF processor for RAG (optional - fail gracefully if not available)
try:
    from pdf_processor import PDFProcessor
    RAG_AVAILABLE = True
    print("✓ RAG integration enabled for manual deletion", flush=True)
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠ RAG integration disabled: {e}", flush=True)

# Initialize RAG processor if available (module-level, persistent)
rag_processor = None
if RAG_AVAILABLE:
    try:
        rag_processor = PDFProcessor()
        print("✓ RAG processor initialized", flush=True)
    except Exception as e:
        print(f"⚠ RAG processor initialization failed: {e}", flush=True)
        rag_processor = None

class HistoryAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/history/conversations':
            self.get_conversations()
        elif self.path == '/history/manuals':
            self.get_manuals()
        elif self.path == '/history/stats':
            self.get_stats()
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/history/conversation/'):
            conv_id = self.path.split('/')[-1]
            self.delete_conversation(conv_id)
        elif self.path.startswith('/history/manual/'):
            filename = self.path.split('/')[-1]
            self.delete_manual(filename)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def get_conversations(self):
        """Get all conversations from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get conversations
            cursor.execute("""
                SELECT id, timestamp, question, answer, ai_used, provider, model,
                       response_time_ms, user_rating, important
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT 100
            """)

            conversations = [dict(row) for row in cursor.fetchall()]

            # Get stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN ai_used='online' THEN 1 ELSE 0 END) as online,
                    SUM(CASE WHEN ai_used='onboard' THEN 1 ELSE 0 END) as onboard
                FROM conversations
            """)

            stats_row = cursor.fetchone()
            stats = {
                'total': stats_row['total'],
                'online': stats_row['online'] or 0,
                'onboard': stats_row['onboard'] or 0
            }

            conn.close()

            self.send_json_response({
                'success': True,
                'conversations': conversations,
                'stats': stats
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def delete_conversation(self, conv_id):
        """Delete a conversation from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))

            conn.commit()
            conn.close()

            self.send_json_response({
                'success': True,
                'message': 'Conversation deleted'
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def get_manuals(self):
        """Get list of uploaded manuals"""
        try:
            manuals = []

            if os.path.exists(MANUALS_DIR):
                for filename in os.listdir(MANUALS_DIR):
                    if filename.endswith('.pdf'):
                        filepath = os.path.join(MANUALS_DIR, filename)
                        stat = os.stat(filepath)

                        manuals.append({
                            'filename': filename,
                            'size': stat.st_size,
                            'uploaded': stat.st_mtime,
                            'path': filepath
                        })

            # Sort by upload time (newest first)
            manuals.sort(key=lambda x: x['uploaded'], reverse=True)

            self.send_json_response({
                'success': True,
                'manuals': manuals,
                'count': len(manuals)
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def delete_manual(self, filename):
        """Delete an uploaded manual from filesystem and RAG database"""
        try:
            # Sanitize filename
            filename = os.path.basename(filename)
            filepath = os.path.join(MANUALS_DIR, filename)

            if not os.path.exists(filepath):
                self.send_json_response({
                    'success': False,
                    'error': 'Manual not found'
                }, 404)
                return

            if not filepath.endswith('.pdf'):
                self.send_json_response({
                    'success': False,
                    'error': 'Invalid file type'
                }, 400)
                return

            # Delete from RAG database first (before deleting file)
            rag_deleted = False
            rag_error = None

            if rag_processor:
                try:
                    print(f"🗑️ Removing from RAG database: {filename}", flush=True)
                    rag_result = rag_processor.delete_document(filename)

                    if rag_result.get('success'):
                        print(f"✓ Removed from RAG: {filename}", flush=True)
                        rag_deleted = True
                    else:
                        rag_error = rag_result.get('error', 'Unknown RAG error')
                        print(f"⚠ RAG deletion failed: {rag_error}", flush=True)
                        # Continue with file deletion even if RAG fails

                except Exception as e:
                    rag_error = str(e)
                    print(f"⚠ RAG deletion error: {e}", flush=True)
                    # Continue with file deletion even if RAG fails
            else:
                print(f"⚠ RAG not available - only deleting file", flush=True)

            # Delete file from filesystem
            os.remove(filepath)
            print(f"✓ Deleted file: {filename}", flush=True)

            # Prepare response
            response = {
                'success': True,
                'message': f'Manual {filename} deleted',
                'rag_deleted': rag_deleted
            }

            if rag_error:
                response['warning'] = f'File deleted but RAG removal failed: {rag_error}'

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def get_stats(self):
        """Get system statistics"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Conversation stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(response_time_ms) as avg_response_time,
                    MAX(timestamp) as last_query
                FROM conversations
            """)

            row = cursor.fetchone()

            # Manual count
            manual_count = 0
            if os.path.exists(MANUALS_DIR):
                manual_count = len([f for f in os.listdir(MANUALS_DIR) if f.endswith('.pdf')])

            conn.close()

            self.send_json_response({
                'success': True,
                'stats': {
                    'total_conversations': row[0],
                    'avg_response_time_ms': row[1] or 0,
                    'last_query': row[2],
                    'manuals_uploaded': manual_count
                }
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

def main():
    server = HTTPServer(('0.0.0.0', PORT), HistoryAPIHandler)
    print(f"History API server running on port {PORT}")
    server.serve_forever()

if __name__ == '__main__':
    main()
