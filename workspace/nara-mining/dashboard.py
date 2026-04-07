#!/usr/bin/env python3
"""
NARA Mining Dashboard - Real-time Web Monitor
"""
import json
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify
import threading
import time

app = Flask(__name__)

STATS_FILE = Path.home() / ".nara-mining-stats.json"
WALLET_DIR = Path.home() / ".nara-wallets"
DASHBOARD_PORT = 8080

def load_stats():
    """Load mining stats"""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "total_wallets": 30,
        "active_wallets": [],
        "rotation_count": 0,
        "submissions": {},
        "start_time": None
    }

def get_wallet_count():
    """Count wallets"""
    try:
        return len(list(WALLET_DIR.glob("W*.json")))
    except:
        return 0

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🖤 NARA Mining Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0d0d0d;
            color: #e0e0e0;
            font-family: 'Segoe UI', monospace;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #333;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #ff006e, #8338ec);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(145deg, #1a1a1a, #0f0f0f);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #333;
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: #ff006e;
        }
        .stat-label {
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
        }
        .stat-value.success { color: #00ff88; }
        .stat-value.warning { color: #ffaa00; }
        .stat-value.error { color: #ff006e; }
        
        .section {
            background: #1a1a1a;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        .section h2 {
            color: #8338ec;
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        
        .wallet-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .wallet-tag {
            background: #333;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            border: 1px solid #555;
        }
        .wallet-tag.active {
            background: linear-gradient(45deg, #ff006e, #8338ec);
            border-color: transparent;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .log-container {
            background: #0a0a0a;
            border-radius: 10px;
            padding: 15px;
            font-family: monospace;
            font-size: 0.85em;
            max-height: 300px;
            overflow-y: auto;
            color: #00ff88;
        }
        .log-line {
            padding: 3px 0;
            border-bottom: 1px solid #222;
        }
        
        .refresh-info {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 0.9em;
        }
        
        .progress-bar {
            background: #333;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff006e, #8338ec);
            transition: width 0.5s;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🖤 NARA Mining Dashboard</h1>
        <p>Real-time Multi-Wallet PoMI Monitor</p>
    </div>
    
    <div class="stats-grid" id="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Wallets</div>
            <div class="stat-value" id="total-wallets">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Active Miners</div>
            <div class="stat-value success" id="active-miners">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Submissions</div>
            <div class="stat-value warning" id="total-submissions">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Rotations</div>
            <div class="stat-value" id="rotations">-</div>
        </div>
    </div>
    
    <div class="section">
        <h2>🖤 Active Wallets (Current Rotation)</h2>
        <div class="wallet-list" id="active-wallets">
            Loading...
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Submissions per Wallet</h2>
        <div id="submissions-chart">
            Loading...
        </div>
    </div>
    
    <div class="section">
        <h2>📜 Recent Activity</h2>
        <div class="log-container" id="activity-log">
            Waiting for data...
        </div>
    </div>
    
    <div class="refresh-info">
        Auto-refresh every 5 seconds | Dashboard runs on port 8080
    </div>
    
    <script>
        async function refreshData() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // Update stats
                document.getElementById('total-wallets').textContent = data.total_wallets || 30;
                document.getElementById('active-miners').textContent = (data.active_wallets || []).length;
                
                const subs = Object.values(data.submissions || {});
                const totalSubs = subs.reduce((a, b) => a + b, 0);
                document.getElementById('total-submissions').textContent = totalSubs;
                
                document.getElementById('rotations').textContent = data.rotation_count || 0;
                
                // Update active wallets
                const activeHtml = (data.active_wallets || []).map(w => 
                    `<span class="wallet-tag active">${w}</span>`
                ).join('');
                document.getElementById('active-wallets').innerHTML = activeHtml || '<span style="color:#666">No active miners</span>';
                
                // Update submissions chart
                const subsEntries = Object.entries(data.submissions || {});
                if (subsEntries.length > 0) {
                    const maxSubs = Math.max(...subsEntries.map(e => e[1]));
                    const chartHtml = subsEntries
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 10)
                        .map(([wallet, count]) => {
                            const pct = (count / maxSubs * 100) || 0;
                            return `<div style="margin-bottom:10px;">
                                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                                    <span>${wallet}</span>
                                    <span>${count} subs</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width:${pct}%"></div>
                                </div>
                            </div>`;
                        }).join('');
                    document.getElementById('submissions-chart').innerHTML = chartHtml;
                } else {
                    document.getElementById('submissions-chart').innerHTML = '<span style="color:#666">No submissions yet</span>';
                }
                
                // Update log
                if (data.recent_logs && data.recent_logs.length > 0) {
                    const logHtml = data.recent_logs.map(line => 
                        `<div class="log-line">${line}</div>`
                    ).join('');
                    document.getElementById('activity-log').innerHTML = logHtml;
                }
                
            } catch (err) {
                console.error('Refresh failed:', err);
            }
        }
        
        // Initial load
        refreshData();
        
        // Auto refresh every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
    ''')

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    stats = load_stats()
    
    # Add recent log lines if available
    log_file = get_latest_log()
    if log_file:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-20:]  # Last 20 lines
                stats['recent_logs'] = [line.strip() for line in lines if line.strip()]
        except:
            pass
    
    return jsonify(stats)

def get_latest_log():
    """Find latest mining log"""
    try:
        log_dir = Path.cwd()
        logs = sorted(log_dir.glob("nara_multi_*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
        return logs[0] if logs else None
    except:
        return None

def run_dashboard():
    """Run Flask dashboard"""
    print(f"🖤 Dashboard starting on http://0.0.0.0:{DASHBOARD_PORT}")
    app.run(host='0.0.0.0', port=DASHBOARD_PORT, debug=False, threaded=True)

if __name__ == '__main__':
    run_dashboard()
