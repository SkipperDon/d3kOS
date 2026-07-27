#!/usr/bin/env python3
"""
d3kOS Manual Management API
Handles manual upload, search, and management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
from pathlib import Path
import time

app = Flask(__name__)
CORS(app)

MANUALS_DIR = Path("/opt/d3kos/data/manuals")
SEARCH_SCRIPT = Path("/opt/d3kos/services/manuals/auto-search.py")

@app.route('/manuals/auto-search', methods=['POST'])
def auto_search():
    """Trigger automatic manual search based on wizard config"""
    try:
        config = request.get_json()
        
        if not config:
            return jsonify({"error": "No configuration provided"}), 400
        
        # Convert config to JSON string for command line
        config_json = json.dumps(config)
        
        # Run search script
        result = subprocess.run(
            [str(SEARCH_SCRIPT), config_json],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # Parse results from stdout
        output = result.stdout
        
        # Extract JSON from output (after separator line)
        if "=" * 60 in output:
            json_str = output.split("=" * 60)[1].strip()
            results = json.loads(json_str)
        else:
            results = {
                "searched": [],
                "found": [],
                "downloaded": [],
                "failed": [],
                "error": "Could not parse results"
            }
        
        return jsonify({
            "success": True,
            "results": results,
            "output": output
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Search timeout (>2 minutes)"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/manuals/list', methods=['GET'])
def list_manuals():
    """List all downloaded manuals"""
    try:
        MANUALS_DIR.mkdir(parents=True, exist_ok=True)
        
        manuals = []
        for pdf in MANUALS_DIR.glob("*.pdf"):
            stat = pdf.stat()
            manuals.append({
                "filename": pdf.name,
                "size": stat.st_size,
                "uploaded": int(stat.st_mtime)
            })
        
        return jsonify({
            "success": True,
            "count": len(manuals),
            "manuals": manuals
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/manuals/delete/<filename>', methods=['DELETE'])
def delete_manual(filename):
    """Delete a manual"""
    try:
        pdf_path = MANUALS_DIR / filename
        
        if not pdf_path.exists():
            return jsonify({
                "success": False,
                "error": "Manual not found"
            }), 404
        
        # Delete file
        pdf_path.unlink()
        
        return jsonify({
            "success": True,
            "message": f"Deleted {filename}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Create directories
    MANUALS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run server
    app.run(host='0.0.0.0', port=8083, debug=False)
