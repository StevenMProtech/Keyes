from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

SUBMISSIONS_FILE = 'submissions.json'

def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_submissions(submissions):
    with open(SUBMISSIONS_FILE, 'w') as f:
        json.dump(submissions, f, indent=2)

@app.route('/test')
def test_page():
    with open('email_template.html', 'r') as f:
        email_html = f.read()
    return email_html

@app.route('/')
def index():
    submissions = load_submissions()
    total = len(submissions)
    pending = sum(1 for s in submissions if s.get('status') == 'pending')
    maximize = sum(1 for s in submissions if s.get('equity_priority') == 'maximize')
    speed = sum(1 for s in submissions if s.get('equity_priority') == 'speed')
    balance = sum(1 for s in submissions if s.get('equity_priority') == 'balance')
    
    # Load email template
    with open('email_template.html', 'r') as f:
        email_html = f.read()
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>The Keyes Company Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #1a1a1a;
            min-height: 100vh;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: 350px 1fr;
            height: 100vh;
        }}
        .sidebar {{
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
            padding: 30px;
            border-right: 1px solid #333;
            display: flex;
            flex-direction: column;
            width: 350px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
        }}
        .logo span {{ color: #fcbfa7; }}
        .tagline {{
            color: #999;
            font-size: 14px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #333;
        }}
        .stat-card {{
            background: rgba(0, 66, 55, 0.15);
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #fcbfa7;
        }}
        .stat-card h3 {{
            color: #999;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }}
        .stat-card .number {{
            font-size: 28px;
            font-weight: 700;
            color: #fcbfa7;
            line-height: 1;
        }}
        .stat-card .label {{
            color: #999;
            font-size: 12px;
            margin-top: 5px;
        }}
        .stats-container {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
        }}
        .actions {{
            margin-top: auto;
            padding-top: 20px;
            border-top: 1px solid #333;
            flex-shrink: 0;
        }}
        .actions h3 {{
            color: white;
            font-size: 14px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .btn {{
            display: block;
            padding: 12px 20px;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin-bottom: 10px;
            text-align: center;
            transition: all 0.2s;
            font-size: 14px;
        }}
        .btn:hover {{ transform: translateX(5px); }}
        .btn.secondary {{
            background: linear-gradient(135deg, #fcbfa7 0%, #f7f3e5 100%);
        }}
        .btn.outline {{
            background: transparent;
            border: 2px solid #004237;
        }}
        .preview {{
            background: #f5f5f5;
            overflow-y: auto;
            padding: 40px 20px;
        }}
        .preview-header {{
            background: white;
            padding: 20px 30px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .preview-header h2 {{
            color: #333;
            font-size: 20px;
        }}
        .preview-header .badge {{
            background: #004237;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .zoom-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .zoom-btn {{
            background: #f0f0f0;
            border: 1px solid #ddd;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .zoom-btn:hover {{
            background: #e0e0e0;
        }}
        .zoom-level {{
            font-size: 12px;
            color: #666;
            min-width: 45px;
            text-align: center;
        }}
        .email-container {{
            max-width: 650px;
            margin: 0 auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        @media (max-width: 1024px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                border-right: none;
                border-bottom: 1px solid #333;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <div class="logo">The <span style="font-style: italic; font-family: Georgia, serif;">Keyes</span> Company</div>
            <div class="tagline">Your Home Equity Campaign Dashboard</div>
            
            <div class="stats-container">
            <div class="stat-card">
                <h3>Total Submissions</h3>
                <div class="number">{total}</div>
                <div class="label">All time</div>
            </div>
            
            <div class="stat-card">
                <h3>Pending Review</h3>
                <div class="number">{pending}</div>
                <div class="label">Needs follow-up</div>
            </div>
            
            <div class="stat-card">
                <h3>Maximize Priority</h3>
                <div class="number">{maximize}</div>
                <div class="label">Want $788k</div>
            </div>
            
            <div class="stat-card">
                <h3>Speed Priority</h3>
                <div class="number">{speed}</div>
                <div class="label">Quick sale</div>
            </div>
            
            <div class="stat-card">
                <h3>Balanced</h3>
                <div class="number">{balance}</div>
                <div class="label">Best of both</div>
            </div>
            </div>
            
            <div class="actions">
                <h3>Quick Actions</h3>
                <a href="/submissions" class="btn">View All Submissions</a>
                <a href="/export" class="btn secondary">Export to CSV</a>
                <a href="/api/submissions" class="btn outline">API (JSON)</a>
            </div>
        </div>
        
        <div class="preview">
            <div class="preview-header">
                <div>
                    <h2>Live Email Campaign Preview</h2>
                </div>
                <div class="zoom-controls">
                    <button class="zoom-btn" onclick="zoomOut()">−</button>
                    <span class="zoom-level" id="zoomLevel">100%</span>
                    <button class="zoom-btn" onclick="zoomIn()">+</button>
                    <div class="badge">LIVE & TESTABLE</div>
                </div>
            </div>
            <script>
                let currentZoom = 1.0;
                function zoomIn() {{
                    if (currentZoom < 1.5) {{
                        currentZoom += 0.1;
                        updateZoom();
                    }}
                }}
                function zoomOut() {{
                    if (currentZoom > 0.5) {{
                        currentZoom -= 0.1;
                        updateZoom();
                    }}
                }}
                function updateZoom() {{
                    document.querySelector('.email-container').style.zoom = currentZoom;
                    document.getElementById('zoomLevel').textContent = Math.round(currentZoom * 100) + '%';
                }}
            </script>
            <div class="email-container">
                {email_html}
            </div>
        </div>
    </div>
</body>
</html>"""

@app.route('/api/submit', methods=['POST', 'OPTIONS'])
def submit_form():
    if request.method == 'OPTIONS':
        return '', 200
    
    submissions = load_submissions()
    
    new_submission = {
        'id': len(submissions) + 1,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': request.form.get('email', ''),
        'first_name': request.form.get('firstName', ''),
        'last_name': request.form.get('lastName', ''),
        'equity_priority': request.form.get('equity_priority', ''),
        'goals': ','.join(request.form.getlist('goals')),
        'goals_text': request.form.get('goalsText', ''),
        'phone_number': request.form.get('phoneNumber', ''),
        'wants_equity_report': request.form.get('wantsReport') == 'yes',
        'wants_expert_contact': request.form.get('wantsExpert') == 'yes',
        'status': 'pending'
    }
    
    submissions.insert(0, new_submission)
    save_submissions(submissions)
    
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You - The Keyes Company</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            background: white;
            padding: 60px 40px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            text-align: center;
        }
        .logo { margin-bottom: 30px; }
        .logo img { width: 180px; height: auto; }
        .checkmark {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
        }
        .checkmark::after {
            content: "✓";
            font-size: 48px;
            color: white;
            font-weight: bold;
        }
        h1 { color: #004237; font-size: 36px; margin-bottom: 20px; }
        p { color: #666; font-size: 18px; line-height: 1.6; margin-bottom: 15px; }
        .highlight {
            background: rgba(252, 191, 167, 0.1);
            padding: 25px;
            border-radius: 12px;
            margin-top: 30px;
            border-left: 4px solid #fcbfa7;
        }
        .footer { margin-top: 40px; font-size: 14px; color: #999; font-style: italic; }
        .back-btn {
            display: inline-block;
            margin-top: 30px;
            padding: 12px 24px;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo"><img src="https://raw.githubusercontent.com/StevenMProtech/Keyes/main/keyes-new-logo.png" alt="Keyes"></div>
        <div class="checkmark"></div>
        <h1>Thank You!</h1>
        <p><strong>Your equity strategy request has been received.</strong></p>
        <p>A Keyes equity expert will review your goals and contact you shortly.</p>
        <div class="highlight">
            <p><strong style="color: #004237; display: block; margin-bottom: 10px;">What's Next?</strong>
            We'll show you how our 4,000+ agent network, exclusive pre-MLS exposure, and nearly 100 years of Florida expertise can help you capture the high end of your equity range.</p>
        </div>
        <div class="footer">Your Fresh Start, Starts Here</div>
        <a href="/" class="back-btn">← Back to Dashboard</a>
    </div>
</body>
</html>"""

@app.route('/submissions')
def view_submissions():
    submissions = load_submissions()
    rows_html = ""
    
    for sub in submissions:
        priority_badge = {
            'maximize': '<span style="background: #004237; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px;">MAXIMIZE</span>',
            'speed': '<span style="background: #fcbfa7; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px;">SPEED</span>',
            'balance': '<span style="background: #666; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px;">BALANCED</span>'
        }.get(sub.get('equity_priority', ''), sub.get('equity_priority', ''))
        
        rows_html += f"""<tr>
            <td>{sub.get('id', '')}</td>
            <td>{sub.get('timestamp', '')}</td>
            <td><strong>{sub.get('email', '')}</strong></td>
            <td>{sub.get('first_name', '')} {sub.get('last_name', '')}</td>
            <td>{priority_badge}</td>
            <td>{sub.get('goals', '')}</td>
            <td>{sub.get('goals_text', '')}</td>
            <td>{sub.get('phone_number', '')}</td>
            <td>{'✓' if sub.get('wants_equity_report') else '—'}</td>
            <td>{'✓' if sub.get('wants_expert_contact') else '—'}</td>
        </tr>"""
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>All Submissions</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8f5e3 100%);
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-left {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .logo {{
            font-size: 24px;
            font-weight: 700;
            opacity: 0.95;
        }}
        .logo span {{ color: #fcbfa7; }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header a {{ color: white; text-decoration: none; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 6px; }}
        table {{ width: 100%; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        th {{ background: #004237; color: white; padding: 16px 12px; text-align: left; }}
        td {{ padding: 14px 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f0f8ed; }}
        .zoom-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .zoom-btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .zoom-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .zoom-level {{
            font-size: 12px;
            color: white;
            min-width: 45px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div class="logo">The <span style="font-style: italic; font-family: Georgia, serif;">Keyes</span> Company</div>
            <h1>All Submissions</h1>
        </div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut()">−</button>
                <span class="zoom-level" id="zoomLevel">100%</span>
                <button class="zoom-btn" onclick="zoomIn()">+</button>
            </div>
            <a href="/">← Dashboard</a>
        </div>
    </div>
    <table>
        <tr>
            <th>ID</th><th>Time</th><th>Email</th><th>Name</th><th>Priority</th><th>Goals</th><th>Details</th><th>Phone</th><th>Report</th><th>Call Past Client</th>
        </tr>
        {rows_html if rows_html else '<tr><td colspan="10" style="text-align: center; padding: 60px; color: #999;">No submissions yet</td></tr>'}
    </table>
    <script>
        let currentZoom = 1.0;
        function zoomIn() {{
            if (currentZoom < 1.5) {{
                currentZoom += 0.1;
                updateZoom();
            }}
        }}
        function zoomOut() {{
            if (currentZoom > 0.5) {{
                currentZoom -= 0.1;
                updateZoom();
            }}
        }}
        function updateZoom() {{
            document.querySelector('table').style.zoom = currentZoom;
            document.getElementById('zoomLevel').textContent = Math.round(currentZoom * 100) + '%';
        }}
    </script>
</body>
</html>"""

@app.route('/api/submissions')
def get_submissions():
    return jsonify(load_submissions())

@app.route('/export')
def export_csv():
    submissions = load_submissions()
    csv = "ID,Timestamp,Email,First Name,Last Name,Equity Priority,Goals,Goals Text,Phone,Wants Report,Wants Expert\n"
    
    for sub in submissions:
        csv += f"{sub.get('id','')},{sub.get('timestamp','')},{sub.get('email','')},{sub.get('first_name','')},{sub.get('last_name','')},{sub.get('equity_priority','')},\"{sub.get('goals','')}\",\"{sub.get('goals_text','')}\",{sub.get('phone_number','')},{sub.get('wants_equity_report','')},{sub.get('wants_expert_contact','')}\n"
    
    return Response(csv, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=keyes.csv"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)



