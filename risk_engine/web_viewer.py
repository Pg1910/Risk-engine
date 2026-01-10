"""
Web-based visualization server for Risk Engine.
Launches a local web server to display charts and graphs.
"""

import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading


class RiskEngineWebHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for Risk Engine web interface."""
    
    def __init__(self, *args, output_dir=None, **kwargs):
        self.output_dir = output_dir
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.send_dashboard()
        elif parsed_path.path == '/api/summary':
            self.send_summary()
        elif parsed_path.path == '/api/flagged':
            self.send_flagged_data()
        elif parsed_path.path.endswith('.png'):
            self.send_image(parsed_path.path)
        else:
            super().do_GET()
    
    def send_dashboard(self):
        """Send the main dashboard HTML."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Risk Engine - Analytics Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0f172a;
            --secondary: #1e293b;
            --accent: #3b82f6;
            --danger: #ef4444;
            --success: #10b981;
            --warning: #f59e0b;
            --text: #f1f5f9;
            --text-secondary: #94a3b8;
            --border: #334155;
            --card-bg: #1e293b;
            --hover: #334155;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--primary);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }
        
        /* Top Navigation */
        .navbar {
            background: var(--secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .nav-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .nav-brand h1 {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text);
        }
        
        .nav-brand .icon {
            font-size: 2rem;
        }
        
        .nav-info {
            display: flex;
            gap: 2rem;
            align-items: center;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 9999px;
            color: var(--success);
            font-weight: 500;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Main Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Stats Cards Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--success));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .stat-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .stat-title {
            font-size: 0.875rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }
        
        .stat-value {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.5rem;
        }
        
        .stat-change {
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .stat-change.positive { color: var(--success); }
        .stat-change.negative { color: var(--danger); }
        
        /* Main Content Cards */
        .content-grid {
            display: grid;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: border-color 0.3s;
        }
        
        .card:hover {
            border-color: var(--accent);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            justify-content: between;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        /* Table Styles */
        .table-container {
            overflow-x: auto;
            border-radius: 8px;
        }
        
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        
        thead {
            background: rgba(59, 130, 246, 0.1);
        }
        
        th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.875rem;
            color: var(--text);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid var(--border);
        }
        
        td {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            color: var(--text-secondary);
        }
        
        tbody tr {
            transition: background-color 0.2s;
        }
        
        tbody tr:hover {
            background: var(--hover);
        }
        
        tbody tr:last-child td {
            border-bottom: none;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .risk-high {
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .risk-medium {
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .risk-low {
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        /* Visualization Grid */
        .viz-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .viz-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .viz-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }
        
        .viz-card img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin-top: 1rem;
            background: white;
            padding: 1rem;
        }
        
        .viz-card h3 {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.5rem;
        }
        
        .viz-description {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        /* Loading State */
        .loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 400px;
            gap: 1rem;
        }
        
        .spinner {
            width: 48px;
            height: 48px;
            border: 4px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Error State */
        .error-card {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            color: var(--danger);
        }
        
        .error-card h3 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            
            .container {
                padding: 1rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .viz-grid {
                grid-template-columns: 1fr;
            }
            
            .stat-value {
                font-size: 1.75rem;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-brand">
            <span class="icon" style="font-weight: bold; color: var(--accent); font-size: 1.5rem;">[RE]</span>
            <h1>Risk Engine Analytics</h1>
        </div>
        <div class="nav-info">
            <div class="status-badge">
                <span class="status-dot"></span>
                Live Monitoring
            </div>
            <span id="last-update">Updated just now</span>
        </div>
    </nav>
    
    <!-- Main Container -->
    <div class="container">
        <div id="content" class="loading">
            <div class="spinner"></div>
            <p>Loading analytics data...</p>
        </div>
    </div>
    
    <script>
        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }
        
        function getRiskBadge(score) {
            if (score >= 5) return '<span class="risk-badge risk-high">High Risk</span>';
            if (score >= 3) return '<span class="risk-badge risk-medium">Medium Risk</span>';
            return '<span class="risk-badge risk-low">Low Risk</span>';
        }
        
        async function loadData() {
            try {
                const summaryRes = await fetch('/api/summary');
                const summary = await summaryRes.json();
                
                const flaggedRes = await fetch('/api/flagged');
                const flagged = await flaggedRes.json();
                
                let html = '';
                
                // Stats Cards
                html += '<div class="stats-grid">';
                
                // Total Transactions
                html += `<div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Total Transactions</span>
                        <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--accent); font-weight: bold;">Σ</div>
                    </div>
                    <div class="stat-value">${formatNumber(summary.total_transactions || 0)}</div>
                    <div class="stat-change">Processed transactions</div>
                </div>`;
                
                // Flagged Transactions
                const flagRate = summary.total_transactions ? 
                    ((summary.total_flagged / summary.total_transactions) * 100).toFixed(2) : 0;
                html += `<div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Flagged Anomalies</span>
                        <div class="stat-icon" style="background: rgba(239, 68, 68, 0.1); color: var(--danger); font-weight: bold;">!</div>
                    </div>
                    <div class="stat-value">${formatNumber(summary.total_flagged || 0)}</div>
                    <div class="stat-change negative">${flagRate}% of total</div>
                </div>`;
                
                // Detection Rate
                html += `<div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Detection Rate</span>
                        <div class="stat-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--success); font-weight: bold;">✓</div>
                    </div>
                    <div class="stat-value">${flagRate}%</div>
                    <div class="stat-change">Anomaly detection accuracy</div>
                </div>`;
                
                // Average Risk Score
                const avgRisk = summary.avg_risk_score ? summary.avg_risk_score.toFixed(2) : 'N/A';
                html += `<div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Avg Risk Score</span>
                        <div class="stat-icon" style="background: rgba(245, 158, 11, 0.1); color: var(--warning); font-weight: bold;">μ</div>
                    </div>
                    <div class="stat-value">${avgRisk}</div>
                    <div class="stat-change">Mean risk level</div>
                </div>`;
                
                html += '</div>';
                
                // Content Grid
                html += '<div class="content-grid">';
                
                // Flagged Transactions Table
                if (flagged && flagged.length > 0) {
                    html += `<div class="card">
                        <div class="card-header">
                            <h2 class="card-title">⚠ High-Risk Transactions</h2>
                        </div>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Transaction ID</th>
                                        <th>Sender Account</th>
                                        <th>Risk Level</th>
                                        <th>Anomaly Reasons</th>
                                    </tr>
                                </thead>
                                <tbody>`;
                    
                    flagged.slice(0, 10).forEach(row => {
                        html += `<tr>
                            <td><strong>${row.transaction_id || 'N/A'}</strong></td>
                            <td>${row.sender_account || 'N/A'}</td>
                            <td>${getRiskBadge(row.risk_score || 0)}</td>
                            <td style="max-width: 400px; white-space: normal;">${row.reasons || 'N/A'}</td>
                        </tr>`;
                    });
                    
                    html += `</tbody></table></div></div>`;
                }
                
                html += '</div>';
                
                // Visualizations
                html += '<div class="viz-grid">';
                
                const vizData = [
                    { file: 'charts/01_anomaly_reasons.png', title: 'Anomaly Breakdown', desc: 'Distribution of anomaly detection reasons' },
                    { file: 'charts/02_risk_score_distribution.png', title: 'Risk Score Distribution', desc: 'Frequency distribution of risk scores' },
                    { file: 'charts/03_hourly_distribution.png', title: 'Temporal Analysis', desc: 'Anomalies detected by hour of day' },
                    { file: 'charts/04_top_accounts.png', title: 'High-Risk Accounts', desc: 'Top accounts by anomaly frequency' },
                    { file: 'charts/05_amount_distribution.png', title: 'Transaction Amounts', desc: 'Distribution of flagged transaction amounts' }
                ];
                
                vizData.forEach(viz => {
                    html += `<div class="viz-card">
                        <h3>${viz.title}</h3>
                        <p class="viz-description">${viz.desc}</p>
                        <img src="/${viz.file}" alt="${viz.title}" onerror="this.parentElement.style.display='none'">
                    </div>`;
                });
                
                html += '</div>';
                
                document.getElementById('content').innerHTML = html;
                document.getElementById('last-update').textContent = 'Updated ' + new Date().toLocaleTimeString();
                
            } catch (error) {
                document.getElementById('content').innerHTML = `
                    <div class="error-card">
                        <h3>⚠ Unable to Load Data</h3>
                        <p>Please ensure the analysis has been completed and output files are available.</p>
                        <p style="margin-top: 1rem; font-size: 0.875rem; opacity: 0.7;">${error.message}</p>
                    </div>`;
                console.error('Error:', error);
            }
        }
        
        loadData();
        setInterval(loadData, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_summary(self):
        """Send summary.json data."""
        summary_file = Path(self.output_dir) / 'summary.json'
        
        if summary_file.exists():
            try:
                data = json.loads(summary_file.read_text())
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                return
            except Exception as e:
                print(f"Error reading summary: {e}")
        
        self.send_response(404)
        self.end_headers()
    
    def send_flagged_data(self):
        """Send flagged transactions data."""
        flagged_file = Path(self.output_dir) / 'flagged_transactions.csv'
        
        if flagged_file.exists():
            try:
                import pandas as pd
                df = pd.read_csv(flagged_file)
                data = df.to_dict('records')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                return
            except Exception as e:
                print(f"Error reading flagged transactions: {e}")
        
        self.send_response(404)
        self.end_headers()
    
    def send_image(self, path):
        """Send image file."""
        image_file = Path(self.output_dir) / path.lstrip('/')
        
        if image_file.exists():
            try:
                with open(image_file, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(f.read())
                return
            except Exception as e:
                print(f"Error sending image: {e}")
        
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def start_web_viewer(output_dir: str, port: int = 8080):
    """
    Start web server to view analysis results.
    
    Args:
        output_dir: Directory containing analysis results
        port: Port to run server on
    """
    output_path = Path(output_dir).resolve()
    
    if not output_path.exists():
        print(f"[ERROR] Output directory not found: {output_dir}")
        return
    
    # Change to output directory
    os.chdir(output_path)
    
    # Create handler with output directory
    handler = lambda *args, **kwargs: RiskEngineWebHandler(*args, output_dir=output_path, **kwargs)
    
    try:
        server = HTTPServer(('localhost', port), handler)
        url = f'http://localhost:{port}'
        
        print(f"\n[SERVER] Web viewer starting at {url}")
        print(f"[INFO] Serving files from: {output_path}")
        print("[INFO] Press Ctrl+C to stop the server\n")
        
        # Open browser
        webbrowser.open(url)
        
        # Start server
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n[SERVER] Server stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n[ERROR] Port {port} is already in use. Try a different port.")
        else:
            print(f"\n[ERROR] Error starting server: {e}")


def start_web_viewer_background(output_dir: str, port: int = 8080):
    """
    Start web viewer in background thread.
    
    Args:
        output_dir: Directory containing analysis results
        port: Port to run server on
    """
    thread = threading.Thread(
        target=start_web_viewer,
        args=(output_dir, port),
        daemon=True
    )
    thread.start()
    return thread
