#!/usr/bin/env python3
"""
d3kOS Manual Auto-Search Service
Automatically searches for and downloads boat/engine manuals
"""

import os
import sys
import json
import time
import requests
import html
import shutil
from urllib.parse import quote_plus, urlparse, unquote
from pathlib import Path

# Configuration
MANUALS_DIR = Path("/opt/d3kos/data/manuals")
REFERENCE_DIR = Path("/opt/d3kos/reference")
SKILLS_FILE = Path("/opt/d3kos/config/skills.md")
SEARCH_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 30
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class ManualSearcher:
    def __init__(self, config):
        """Initialize with wizard configuration data"""
        self.config = config
        self.results = {
            "searched": [],
            "found": [],
            "downloaded": [],
            "failed": []
        }
        
        # Ensure directories exist
        MANUALS_DIR.mkdir(parents=True, exist_ok=True)
        
    def search_all(self):
        """Search for all manuals based on configuration"""
        print("Starting manual search...")
        
        # 1. CX5106 manual (check local first, always include)
        self.search_cx5106_manual()
        
        # 2. Boat owner's manual
        if self.config.get('q1') and self.config.get('q3'):
            self.search_boat_manual()
        
        # 3. Engine service manual
        if self.config.get('q5') and self.config.get('q6'):
            self.search_engine_manual()
        
        return self.results
    
    def search_boat_manual(self):
        """Search for boat owner's manual"""
        manufacturer = self.config.get('q1', '')
        model = self.config.get('q3', '')
        year = self.config.get('q2', '')
        
        query = f"{manufacturer} {model} {year} owner's manual PDF"
        manual_type = "boat"
        filename = f"{manufacturer}_{model}_{year}_owners_manual.pdf".replace(' ', '_')
        
        print(f"Searching for boat manual: {query}")
        self.results['searched'].append(f"Boat: {manufacturer} {model} {year}")
        
        # Web search
        urls = self.web_search(query)
        for url in urls:
            if self.download_manual(url, filename, manual_type):
                return  # Success, stop trying
    
    def search_engine_manual(self):
        """Search for engine service manual"""
        make = self.config.get('q5', '')
        model = self.config.get('q6', '')
        year = self.config.get('q7', '')
        
        query = f"{make} {model} {year} service manual PDF"
        manual_type = "engine"
        filename = f"{make}_{model}_{year}_service_manual.pdf".replace(' ', '_')
        
        print(f"Searching for engine manual: {query}")
        self.results['searched'].append(f"Engine: {make} {model} {year}")
        
        # Web search
        urls = self.web_search(query)
        for url in urls:
            if self.download_manual(url, filename, manual_type):
                return  # Success, stop trying
    
    def search_cx5106_manual(self):
        """Search for CX5106 NMEA2000 gateway manual - check local first"""
        filename = "CX5106_manual.pdf"
        manual_type = "electronics"
        
        print("Checking for CX5106 manual...")
        self.results['searched'].append("CX5106 NMEA2000 Gateway")
        
        # Check if local copy already exists
        local_path = MANUALS_DIR / filename
        if local_path.exists():
            print(f"✓ CX5106 manual already installed: {filename}")
            self.results['found'].append(filename)
            self.results['downloaded'].append({
                "filename": filename,
                "type": manual_type,
                "url": "local",
                "size": local_path.stat().st_size
            })
            
            # Ensure it's in skills.md
            self.process_manual(local_path, manual_type)
            return
        
        # Check reference directory for local copy
        ref_paths = [
            REFERENCE_DIR / "CX5106_10125_manual.pdf",
            REFERENCE_DIR / "CX5106_manual.pdf",
            Path("/tmp/CX5106_10125_manual.pdf")
        ]
        
        for ref_path in ref_paths:
            if ref_path.exists():
                print(f"✓ Found local CX5106 manual, copying to manuals directory")
                shutil.copy2(ref_path, local_path)
                self.results['found'].append(filename)
                self.results['downloaded'].append({
                    "filename": filename,
                    "type": manual_type,
                    "url": "local",
                    "size": local_path.stat().st_size
                })
                self.process_manual(local_path, manual_type)
                return
        
        # If not found locally, try web search
        print("Local CX5106 manual not found, searching online...")
        query = "Maretron CX5106 NMEA2000 gateway manual PDF"
        urls = self.web_search(query)
        for url in urls:
            if self.download_manual(url, filename, manual_type):
                return  # Success
    
    def web_search(self, query):
        """Perform web search and return list of PDF links"""
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(search_url, headers=headers, timeout=SEARCH_TIMEOUT)
            
            if response.status_code == 200:
                content = response.text
                
                # Extract and clean PDF links
                import re
                
                # Look for uddg= parameter in DuckDuckGo redirect links
                uddg_pattern = r'uddg=([^&\'"]+)'
                uddg_matches = re.findall(uddg_pattern, content)
                
                clean_urls = []
                for encoded_url in uddg_matches:
                    # URL decode
                    decoded_url = unquote(encoded_url)
                    # Decode HTML entities
                    decoded_url = html.unescape(decoded_url)
                    # Check if it's a PDF
                    if '.pdf' in decoded_url.lower():
                        # Ensure it has a scheme
                        if decoded_url.startswith('//'):
                            decoded_url = 'https:' + decoded_url
                        elif not decoded_url.startswith('http'):
                            decoded_url = 'https://' + decoded_url
                        
                        clean_urls.append(decoded_url)
                
                # Also look for direct PDF links
                direct_pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
                direct_matches = re.findall(direct_pdf_pattern, content, re.IGNORECASE)
                for url in direct_matches:
                    decoded_url = html.unescape(url)
                    if decoded_url.startswith('//'):
                        decoded_url = 'https:' + decoded_url
                    elif not decoded_url.startswith('http'):
                        continue  # Skip relative URLs
                    clean_urls.append(decoded_url)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_urls = []
                for url in clean_urls:
                    if url not in seen:
                        seen.add(url)
                        unique_urls.append(url)
                
                return unique_urls[:5]  # Return top 5 URLs
            
        except Exception as e:
            print(f"Web search error: {e}")
        
        return []
    
    def download_manual(self, url, filename, manual_type):
        """Download a manual from URL"""
        try:
            print(f"Attempting download: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=DOWNLOAD_TIMEOUT, stream=True, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"Download failed: HTTP {response.status_code}")
                return False
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'html' in content_type:
                print(f"Skipping HTML page: {content_type}")
                return False
            
            # Check file size
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                print(f"File too large: {content_length} bytes")
                return False
            
            # Download to temp file first
            temp_path = MANUALS_DIR / f".{filename}.tmp"
            final_path = MANUALS_DIR / filename
            
            downloaded_size = 0
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if downloaded_size > MAX_FILE_SIZE:
                        print(f"File exceeded size limit during download")
                        temp_path.unlink()
                        return False
            
            # Verify it's actually a PDF
            with open(temp_path, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF'):
                    print(f"Invalid PDF header: {header}")
                    temp_path.unlink()
                    return False
            
            # Move to final location
            temp_path.rename(final_path)
            
            print(f"✓ Downloaded: {filename} ({downloaded_size} bytes)")
            self.results['found'].append(filename)
            self.results['downloaded'].append({
                "filename": filename,
                "type": manual_type,
                "url": url,
                "size": final_path.stat().st_size
            })
            
            # Process manual (extract text, add to skills.md)
            self.process_manual(final_path, manual_type)
            
            return True
            
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def process_manual(self, pdf_path, manual_type):
        """Process downloaded manual - extract text and add to skills.md"""
        try:
            print(f"Processing manual: {pdf_path.name}")
            
            # Check if already in skills.md
            if SKILLS_FILE.exists():
                with open(SKILLS_FILE, 'r') as f:
                    content = f.read()
                    if f"## Manual: {pdf_path.name}" in content:
                        print(f"Manual already indexed in skills.md")
                        return
            
            # Add note to skills.md
            note = f"\n\n## Manual: {pdf_path.name}\n"
            note += f"Type: {manual_type}\n"
            note += f"Location: {pdf_path}\n"
            note += f"Added: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if SKILLS_FILE.exists():
                with open(SKILLS_FILE, 'a') as f:
                    f.write(note)
            
        except Exception as e:
            print(f"Processing error: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: auto-search.py <config_json>")
        sys.exit(1)
    
    # Parse configuration from command line
    try:
        config = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Error: Invalid JSON configuration")
        sys.exit(1)
    
    # Create searcher and run
    searcher = ManualSearcher(config)
    results = searcher.search_all()
    
    # Output results as JSON
    print("\n" + "="*60)
    print(json.dumps(results, indent=2))
    
    # Return success if we found at least one manual
    return 0 if results['downloaded'] else 1

if __name__ == '__main__':
    sys.exit(main())
