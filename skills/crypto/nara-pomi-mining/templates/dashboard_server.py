#!/usr/bin/env python3
"""
NARA Dashboard Server - Accessible from anywhere
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
HOST = "0.0.0.0"  # Listen on all interfaces

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"🖤 [{self.log_date_time_string()}] {self.address_string()} - {format%args}")
    
    def do_GET(self):
        if self.path == "/":
            self.path = "/dashboard.html"
        super().do_GET()
    
    def end_headers(self):
        # CORS headers for external access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    os.chdir(Path(__file__).parent)
    
    # Get IPs
    import socket
    hostname = socket.gethostname()
    ips = []
    try:
        for addr in socket.getaddrinfo(hostname, None):
            ip = addr[4][0]
            if not ip.startswith('127.') and ':' not in ip:
                ips.append(ip)
    except:
        pass
    
    print("\n" + "="*60)
    print("🖤 NARA MINING DASHBOARD SERVER")
    print("="*60)
    print(f"\n📊 Dashboard URLs:")
    print(f"   Local:    http://localhost:{PORT}")
    print(f"   Network:  http://0.0.0.0:{PORT}")
    for ip in ips:
        print(f"   External: http://{ip}:{PORT}")
    print(f"\n🚀 Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    with socketserver.TCPServer((HOST, PORT), DashboardHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    main()
