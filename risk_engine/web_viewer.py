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
<html>
<head>
    <title>Risk Engine - Visualization Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .subtitle { color: #666; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .stat:last-child { border-bottom: none; }
        .stat-label { color: #666; }
        .stat-value { font-weight: bold; color: #333; }
        .alert { background: #fef5e7; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .image-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .image-card h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .image-card img {
            width: 100%;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: white;
            font-size: 1.2em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }
        tr:hover { background: #f8f9fa; }
        .error-msg {
            color: #e74c3c;
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Risk Engine - Visualization Dashboard</h1>
            <p class="subtitle">Transaction Anomaly Detection Results</p>
        </div>
        
        <div id="content" class="loading">
            Loading data...
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                const summaryRes = await fetch('/api/summary');
                const summary = await summaryRes.json();
                
                let html = '<div class="grid">';
                
                // Summary Stats
                html += '<div class="card"><h2>📊 Summary</h2>';
                for (const [key, value] of Object.entries(summary)) {
                    const label = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                    html += `<div class="stat"><span class="stat-label">${label}</span><span class="stat-value">${value}</span></div>`;
                }
                html += '</div>';
                
                html += '</div>';
                
                // Flagged Transactions
                try {
                    const flaggedRes = await fetch('/api/flagged');
                    const flagged = await flaggedRes.json();
                    
                    if (flagged.length > 0) {
                        html += '<div class="card"><h2>🚨 Flagged Transactions (Top 10)</h2>';
                        html += '<div style="overflow-x: auto;"><table>';
                        html += '<tr><th>Transaction ID</th><th>Risk Score</th><th>Reasons</th></tr>';
                        
                        flagged.slice(0, 10).forEach(row => {
                            html += `<tr>`;
                            html += `<td>${row.transaction_id || 'N/A'}</td>`;
                            html += `<td>${row.risk_score || 'N/A'}</td>`;
                            html += `<td>${row.reasons || 'N/A'}</td>`;
                            html += `</tr>`;
                        });
                        
                        html += '</table></div></div>';
                    }
                } catch (e) {
                    console.error('Could not load flagged transactions:', e);
                }
                
                // Images
                const images = [
                    'risk_score_distribution.png',
                    'top_anomaly_reasons.png',
                    'flagged_vs_normal.png'
                ];
                
                html += '<div class="image-gallery">';
                for (const img of images) {
                    const title = img.replace('.png', '').replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                    html += `<div class="image-card">`;
                    html += `<h3>${title}</h3>`;
                    html += `<img src="/${img}" alt="${title}" onerror="this.parentElement.style.display='none'">`;
                    html += `</div>`;
                }
                html += '</div>';
                
                document.getElementById('content').innerHTML = html;
                
            } catch (error) {
                document.getElementById('content').innerHTML = 
                    '<div class="card error-msg">❌ Error loading data. Make sure the analysis has been run.</div>';
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
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    # Change to output directory
    os.chdir(output_path)
    
    # Create handler with output directory
    handler = lambda *args, **kwargs: RiskEngineWebHandler(*args, output_dir=output_path, **kwargs)
    
    try:
        server = HTTPServer(('localhost', port), handler)
        url = f'http://localhost:{port}'
        
        print(f"\n🌐 Web viewer starting at {url}")
        print(f"📂 Serving files from: {output_path}")
        print("   Press Ctrl+C to stop the server\n")
        
        # Open browser
        webbrowser.open(url)
        
        # Start server
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use. Try a different port.")
        else:
            print(f"\n❌ Error starting server: {e}")


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
