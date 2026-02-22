#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# Fish Detector Service Diagnostic & Fix Script
# Auto-detects and fixes common fish detection issues

set -e

echo "==============================================="
echo "  d3kOS Fish Detector Diagnostic & Fix Tool"
echo "==============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Do not run as root. Run as d3kos user."
    exit 1
fi

echo "Step 1: Checking Python dependencies..."

# Check onnxruntime
if python3 -c "import onnxruntime" 2>/dev/null; then
    VERSION=$(python3 -c "import onnxruntime; print(onnxruntime.__version__)")
    success "ONNX Runtime installed (version $VERSION)"
else
    warning "ONNX Runtime not found, installing..."
    pip3 install onnxruntime
    success "ONNX Runtime installed"
fi

# Check numpy
if python3 -c "import numpy" 2>/dev/null; then
    VERSION=$(python3 -c "import numpy; print(numpy.__version__)")
    success "NumPy installed (version $VERSION)"
else
    warning "NumPy not found, installing..."
    pip3 install numpy
    success "NumPy installed"
fi

# Check Pillow
if python3 -c "from PIL import Image" 2>/dev/null; then
    success "Pillow (PIL) installed"
else
    warning "Pillow not found, installing..."
    pip3 install pillow
    success "Pillow installed"
fi

echo ""
echo "Step 2: Checking YOLOv8 model file..."

MODEL_PATH="/opt/d3kos/models/marine-vision/yolov8n.onnx"
MODEL_DIR="/opt/d3kos/models/marine-vision"

# Create directory if doesn't exist
mkdir -p "$MODEL_DIR"

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    warning "Model file missing, downloading..."
    cd "$MODEL_DIR"
    wget -q --show-progress https://storage.googleapis.com/ailia-models/yolov8/yolov8n.onnx
    success "Model downloaded"
else
    # Check model size
    SIZE=$(stat -c%s "$MODEL_PATH")
    SIZE_MB=$((SIZE / 1024 / 1024))

    if [ $SIZE -lt 10000000 ]; then
        warning "Model file too small ($SIZE_MB MB), re-downloading..."
        rm -f "$MODEL_PATH"
        cd "$MODEL_DIR"
        wget -q --show-progress https://storage.googleapis.com/ailia-models/yolov8/yolov8n.onnx
        success "Model downloaded"
    else
        success "Model file exists ($SIZE_MB MB)"
    fi
fi

echo ""
echo "Step 3: Testing model loading..."

# Test model loading
if python3 <<EOF
import onnxruntime as ort
try:
    session = ort.InferenceSession('$MODEL_PATH')
    print("Model loaded successfully")
    exit(0)
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)
EOF
then
    success "Model loads successfully"
else
    error "Model loading failed"
    exit 1
fi

echo ""
echo "Step 4: Checking database..."

DB_PATH="/opt/d3kos/data/marine-vision/captures.db"
DB_DIR="/opt/d3kos/data/marine-vision"

mkdir -p "$DB_DIR"

if [ -f "$DB_PATH" ]; then
    # Check database integrity
    if sqlite3 "$DB_PATH" "PRAGMA integrity_check;" | grep -q "ok"; then
        success "Database integrity OK"
    else
        warning "Database corrupted, backing up and recreating..."
        mv "$DB_PATH" "${DB_PATH}.bak.$(date +%Y%m%d%H%M%S)"
        warning "Database will be recreated on next service start"
    fi
else
    warning "Database doesn't exist yet (will be created on first run)"
fi

echo ""
echo "Step 5: Checking camera connection..."

# Check camera stream service
if systemctl is-active --quiet d3kos-camera-stream.service; then
    success "Camera stream service running"

    # Test camera ping
    if ping -c 1 -W 2 10.42.0.100 >/dev/null 2>&1; then
        success "Camera reachable at 10.42.0.100"
    else
        warning "Camera not responding to ping"
        warning "Check camera power and network connection"
    fi
else
    warning "Camera stream service not running"
    echo "    Attempting to start..."
    sudo systemctl start d3kos-camera-stream.service
    sleep 2
    if systemctl is-active --quiet d3kos-camera-stream.service; then
        success "Camera stream service started"
    else
        error "Camera stream service failed to start"
    fi
fi

echo ""
echo "Step 6: Checking service file..."

SERVICE_FILE="/opt/d3kos/services/marine-vision/fish_detector.py"

if [ -f "$SERVICE_FILE" ]; then
    success "Service file exists"

    # Check for syntax errors
    if python3 -m py_compile "$SERVICE_FILE" 2>/dev/null; then
        success "Service file has no syntax errors"
    else
        error "Service file has Python syntax errors"
        python3 -m py_compile "$SERVICE_FILE"
        exit 1
    fi
else
    error "Service file missing: $SERVICE_FILE"
    exit 1
fi

echo ""
echo "Step 7: Restarting fish detector service..."

sudo systemctl daemon-reload
sudo systemctl restart d3kos-fish-detector.service

# Wait for service to start
sleep 3

# Check service status
if systemctl is-active --quiet d3kos-fish-detector.service; then
    success "Service is running"
else
    error "Service failed to start"
    echo ""
    echo "Recent service logs:"
    journalctl -u d3kos-fish-detector.service -n 20 --no-pager
    exit 1
fi

echo ""
echo "Step 8: Testing API endpoints..."

# Test status endpoint
if curl -s http://localhost:8086/detect/status | grep -q "running"; then
    success "API status endpoint responding"
else
    error "API status endpoint not responding"
    echo "    Trying via curl:"
    curl -v http://localhost:8086/detect/status
    exit 1
fi

# Test nginx proxy
if curl -s http://localhost/detect/status | grep -q "running"; then
    success "Nginx proxy working"
else
    warning "Nginx proxy not configured correctly"
    echo "    Add to /etc/nginx/sites-enabled/default:"
    echo "    location /detect/ {"
    echo "        proxy_pass http://localhost:8086/detect/;"
    echo "    }"
fi

echo ""
echo "==============================================="
echo "  Fish Detector Diagnostic Complete"
echo "==============================================="
echo ""
success "All checks passed!"
echo ""
echo "Service Status:"
systemctl status d3kos-fish-detector.service --no-pager -l | head -10
echo ""
echo "Test the web UI at: http://192.168.1.237/marine-vision.html"
echo ""
