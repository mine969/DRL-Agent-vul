from flask import Flask, request, render_template, redirect, url_for, session, flash
import time
import random
import string

app = Flask(__name__)
app.secret_key = 'hard_mode_secret'

# --- DEFENSES ---

# 1. Rate Limiting
# Simple in-memory store: {ip: [timestamp1, timestamp2, ...]}
request_history = {}
banned_ips = {}
RATE_LIMIT = 5  # requests
TIME_WINDOW = 2 # seconds
BAN_DURATION = 10 # seconds

def check_rate_limit():
    ip = request.remote_addr
    now = time.time()
    
    # Check ban
    if ip in banned_ips:
        if now < banned_ips[ip]:
            return True # Banned
        else:
            del banned_ips[ip] # Unban
            
    # Record request
    if ip not in request_history:
        request_history[ip] = []
    request_history[ip].append(now)
    
    # Clean old requests
    request_history[ip] = [t for t in request_history[ip] if now - t < TIME_WINDOW]
    
    # Check limit
    if len(request_history[ip]) > RATE_LIMIT:
        banned_ips[ip] = now + BAN_DURATION
        return True
        
    return False

# 2. WAF (Web Application Firewall)
BLACKLIST = ["UNION", "SELECT", "script", "alert", "/etc/passwd", "OR", "1=1"]

def check_waf(payload):
    if not payload: return False
    # Simple case-insensitive check (but we can make it strict for "Hard Mode")
    # Real WAFs are smarter, but this forces obfuscation (e.g. SeLeCt vs SELECT)
    # Let's make it case-SENSITIVE for some, insensitive for others to simulate mixed rules
    for bad in BLACKLIST:
        if bad in payload: # Strict check
            return True
    return False

# 3. CSRF Protection
def get_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return session['csrf_token']

@app.before_request
def before_request():
    if check_rate_limit():
        return "429 Too Many Requests - You are banned for 10s", 429

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # CSRF Check
        token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            flash("Invalid CSRF Token", "alert")
            return render_template('login.html', csrf_token=get_csrf_token()), 400
            
        username = request.form.get('username')
        password = request.form.get('password')
        
        # WAF Check
        if check_waf(username) or check_waf(password):
            flash("WAF Blocked Malicious Payload", "alert")
            return render_template('login.html', csrf_token=get_csrf_token()), 403
        
        # VULNERABILITY: SQL Injection (Obfuscation needed)
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        if ("' or '1'='1" in query.lower() and "OR" not in query) or (username == 'admin' and password == 'secret'):
            flash("Welcome Admin! Flag: SQLI_SUCCESS", "success")
            return render_template('login.html', csrf_token=get_csrf_token())
        else:
            flash("Invalid credentials", "alert")
            return render_template('login.html', csrf_token=get_csrf_token())
            
    token = get_csrf_token()
    return render_template('login.html', csrf_token=token)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    if check_waf(query):
        flash("WAF Blocked Malicious Payload", "alert")
        return render_template('search.html', query=query), 403
        
    # VULNERABILITY: Reflected XSS
    # Rendered with | safe in template, so XSS is possible
    return render_template('search.html', query=query)

@app.route('/admin/debug')
def admin_debug():
    return "DEBUG INFO: SECRET_KEY = 'super_secret_key_123'; DB_HOST = 'localhost'"

@app.route('/ping')
def ping():
    ip = request.args.get('ip', '')
    if check_waf(ip):
         return "403 Forbidden - WAF Blocked", 403
         
    if ';' in ip:
        cmd = ip.split(';')[1].strip()
        if 'cat /etc/passwd' in cmd:
            return "root:x:0:0:root:/root:/bin/bash"
    return f"Pinging {ip}..."

@app.route('/profile')
def profile():
    user_id = request.args.get('user_id', '1')
    if user_id == '2':
        return "User Profile: Admin (ID: 2) | Email: admin@example.com"
    return "User Profile: Guest (ID: 1)"

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url', '')
    if 'localhost' in url and '/admin/debug' in url:
        return "DEBUG INFO: SECRET_KEY = 'super_secret_key_123'"
    return f"Fetched {url}"

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000)
