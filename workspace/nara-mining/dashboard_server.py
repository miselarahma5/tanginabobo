#!/usr/bin/env python3
"""
NARA Dashboard Server - Accessible from anywhere
"""
import http.server
import socketserver
import os
from pathlib import Path
import json
import threading
import time

PORT = 8080
HOST = "0.0.0.0"  # Listen on all interfaces
DASHBOARD_FILE = "dashboard.html"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Custom logging
        print(f"🖤 [{self.log_date_time_string()}] {self.address_string()} - {format%args}")
    
    def do_GET(self):
        # Serve dashboard.html for root path
        if self.path == "/":
            self.path = "/dashboard.html"
        
        # Add CORS headers for external access
        super().do_GET()
    
    def end_headers(self):
        # Add CORS headers to allow access from any origin
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

class CORSRequestHandler(DashboardHandler):
    pass

def get_server_ip():
    """Get all IP addresses"""
    import socket
    ips = []
    try:
        # Get hostname
        hostname = socket.gethostname()
        
        # Get all addresses
        for addr in socket.getaddrinfo(hostname, None):
            ip = addr[4][0]
            if not ip.startswith('127.') and ':' not in ip:
                ips.append(ip)
        
        # Also try to get external IP
        import urllib.request
        try:
            external_ip = urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode()
            if external_ip not in ips:
                ips.append(f"EXTERNAL: {external_ip}")
        except:
            pass
            
    except Exception as e:
        print(f"IP detection error: {e}")
    
    return list(set(ips)) if ips else ["localhost"]

def update_stats_file():
    """Create stats file if not exists"""
    stats_file = Path("nara_mining_stats.json")
    if not stats_file.exists():
        sample_stats = {
            "total_wallets": 30,
            "active_wallets": ["W001", "W002", "W003", "W004", "W005"],
            "rotation_count": 0,
            "start_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "submissions": {}
        }
        with open(stats_file, 'w') as f:
            json.dump(sample_stats, f, indent=2)

def main():
    os.chdir(Path(__file__).parent)
    
    # Ensure stats file exists
    update_stats_file()
    
    # Get IP addresses
    ips = get_server_ip()
    
    print("\n" + "="*60)
    print("🖤 NARA MINING DASHBOARD SERVER")
    print("="*60)
    print(f"\n📊 Dashboard URLs:")
    print(f"   Local:    http://localhost:{PORT}")
    print(f"   Network:  http://0.0.0.0:{PORT}")
    for ip in ips:
        print(f"   External: http://{ip}:{PORT}")
    print(f"\n📁 Serving from: {os.getcwd()}")
    print(f"🚀 Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Start server
    with socketserver.TCPServer((HOST, PORT), CORSRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    main()
