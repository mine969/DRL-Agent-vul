from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file
import time
import random
import string
import hashlib
import jwt
import xml.etree.ElementTree as ET
from jinja2 import Template
import os

app = Flask(__name__)
app.secret_key = 'hard_mode_secret'
JWT_SECRET = 'weak_jwt_secret_123'

# --- DEFENSES ---

# 1. Rate Limiting
request_history = {}
banned_ips = {}
RATE_LIMIT = 5
TIME_WINDOW = 2
BAN_DURATION = 10

def check_rate_limit():
    ip = request.remote_addr
    now = time.time()
    
    if ip in banned_ips:
        if now < banned_ips[ip]:
            return True
        else:
            del banned_ips[ip]
            
    if ip not in request_history:
        request_history[ip] = []
    request_history[ip].append(now)
    
    request_history[ip] = [t for t in request_history[ip] if now - t < TIME_WINDOW]
    
    if len(request_history[ip]) > RATE_LIMIT:
        banned_ips[ip] = now + BAN_DURATION
        return True
        
    return False

# 2. WAF
BLACKLIST = ["UNION", "SELECT", "script", "alert", "/etc/passwd", "OR", "1=1", "ENTITY", "DOCTYPE"]

def check_waf(payload):
    if not payload: return False
    for bad in BLACKLIST:
        if bad in payload:
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
        token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            flash("Invalid CSRF Token", "alert")
            return render_template('login.html', csrf_token=get_csrf_token()), 400
            
        username = request.form.get('username')
        password = request.form.get('password')
        
        if check_waf(username) or check_waf(password):
            flash("WAF Blocked Malicious Payload", "alert")
            return render_template('login.html', csrf_token=get_csrf_token()), 403
        
        # VULNERABILITY: SQL Injection
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
    return render_template('search.html', query=query)

# VULNERABILITY: A02 - Cryptographic Failures
@app.route('/download')
def download_file():
    file_id = request.args.get('id', '1')
    # Weak encryption: predictable token
    token = hashlib.md5(file_id.encode()).hexdigest()
    
    if request.args.get('token') == token:
        return f"File {file_id} downloaded! Flag: CRYPTO_FAIL"
    return "Invalid token"

# VULNERABILITY: XXE (XML External Entity)
@app.route('/xml-upload', methods=['POST'])
def xml_upload():
    xml_data = request.data.decode('utf-8')
    
    if check_waf(xml_data):
        return "403 Forbidden - WAF Blocked", 403
    
    try:
        # Vulnerable XML parsing
        root = ET.fromstring(xml_data)
        if 'file://' in xml_data:
            return "XXE Success! Flag: XXE_EXPLOIT"
        return f"Parsed: {root.tag}"
    except:
        return "Invalid XML"

# VULNERABILITY: SSTI (Server-Side Template Injection)
@app.route('/render')
def render_template_vuln():
    name = request.args.get('name', 'Guest')
    
    if check_waf(name):
        return "403 Forbidden - WAF Blocked", 403
    
    # Vulnerable template rendering
    template_str = f"Hello {name}!"
    if '{{' in name:
        try:
            template = Template(template_str)
            result = template.render()
            return f"SSTI Success! Flag: SSTI_EXPLOIT | {result}"
        except:
            return "Template error"
    return template_str

# VULNERABILITY: Path Traversal
@app.route('/files')
def file_access():
    filename = request.args.get('file', 'public.txt')
    
    if check_waf(filename):
        return "403 Forbidden - WAF Blocked", 403
    
    # Vulnerable path handling
    if '../' in filename or '..\\' in filename:
        if 'etc/passwd' in filename or 'secret' in filename:
            return "Path Traversal Success! Flag: PATH_TRAVERSAL | root:x:0:0"
    return f"File: {filename}"

# VULNERABILITY: File Upload (Unrestricted)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file"
    
    file = request.files['file']
    filename = file.filename
    
    # No extension validation
    if filename.endswith('.php') or filename.endswith('.sh'):
        return "Upload Success! Webshell uploaded. Flag: FILE_UPLOAD"
    return "File uploaded"

# VULNERABILITY: JWT Manipulation
@app.route('/api/token', methods=['POST'])
def get_token():
    username = request.json.get('username', 'guest')
    token = jwt.encode({'user': username, 'role': 'user'}, JWT_SECRET, algorithm='HS256')
    return {'token': token}

@app.route('/api/admin')
def admin_api():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if payload.get('role') == 'admin':
            return "JWT Success! Flag: JWT_ADMIN_ACCESS"
        return "Access denied"
    except:
        return "Invalid token"

# VULNERABILITY: NoSQL Injection
@app.route('/api/users')
def nosql_query():
    username = request.args.get('username', '')
    
    # Simulated NoSQL query
    if '[$ne]' in username or '{"$gt":""}' in username:
        return "NoSQL Injection Success! Flag: NOSQL_BYPASS"
    return f"User: {username}"

# VULNERABILITY: A08 - Integrity Failures
@app.route('/update', methods=['POST'])
def software_update():
    package = request.json.get('package', '')
    signature = request.json.get('signature', '')
    
    # No signature verification
    if package and not signature:
        return "Update installed without verification! Flag: INTEGRITY_FAIL"
    return "Update rejected"

# VULNERABILITY: A09 - Logging Failures
@app.route('/admin/delete-user', methods=['POST'])
def delete_user():
    user_id = request.json.get('user_id')
    # Sensitive action not logged
    return f"User {user_id} deleted (no audit log). Flag: LOGGING_FAIL"

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
