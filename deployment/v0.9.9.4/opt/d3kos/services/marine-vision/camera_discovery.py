#!/usr/bin/env python3
"""
Camera Discovery Script
Scans 10.42.0.0/24 for Reolink RLC-810A camera
"""
import socket
import concurrent.futures
import sys
from typing import Optional

def check_rtsp_port(ip: str, port: int = 554, timeout: float = 0.5) -> bool:
    """Check if RTSP port is open"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            return result == 0
    except:
        return False

def scan_network(subnet: str = "10.42.0", start: int = 1, end: int = 254) -> list:
    """Scan network for RTSP cameras"""
    cameras = []

    def check_ip(ip: str):
        if check_rtsp_port(ip):
            return ip
        return None

    print(f"Scanning {subnet}.{start}-{end} for RTSP cameras (port 554)...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        ips = [f"{subnet}.{i}" for i in range(start, end + 1)]
        results = executor.map(check_ip, ips)
        cameras = [ip for ip in results if ip]

    return cameras

def verify_reolink(ip: str, username: str = "d3kos", password: str = "d3kos2026") -> bool:
    """Verify camera is Reolink by testing RTSP URL"""
    import cv2
    rtsp_url = f"rtsp://{username}:{password}@{ip}:554/h264Preview_01_main"

    print(f"Testing RTSP connection to {ip}...")
    cap = cv2.VideoCapture(rtsp_url)
    if cap.isOpened():
        # Try to read a frame to ensure it's actually streaming
        ret, frame = cap.read()
        cap.release()
        return ret and frame is not None
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("d3kOS Marine Vision - Camera Discovery")
    print("=" * 60)
    print()
    
    cameras = scan_network()

    if not cameras:
        print()
        print("✗ No cameras found on 10.42.0.0/24")
        print("  Please verify:")
        print("  - Camera is powered on")
        print("  - Camera is connected to ethernet")
        print("  - Camera is on same network as Pi (10.42.0.x)")
        sys.exit(1)

    print()
    print(f"✓ Found {len(cameras)} camera(s) with RTSP port open: {cameras}")
    print()

    for ip in cameras:
        try:
            if verify_reolink(ip):
                print(f"✓ Reolink camera verified at {ip}")
                print(f"  RTSP URL: rtsp://d3kos:****@{ip}:554/h264Preview_01_main")
                
                # Save to config
                config_path = "/opt/d3kos/config/camera-ip.txt"
                with open(config_path, "w") as f:
                    f.write(ip)
                
                print(f"  Saved to: {config_path}")
                print()
                print("✓ Camera discovery complete!")
                sys.exit(0)
        except Exception as e:
            print(f"✗ Failed to verify {ip}: {e}")
            continue

    print()
    print("✗ No Reolink cameras found that respond to RTSP")
    print("  Found cameras with RTSP port open, but could not connect")
    print("  Please check camera credentials (default: d3kos/d3kos2026)")
    sys.exit(1)
