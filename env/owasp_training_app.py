"""
OWASP Top 10 2025 - Complete Training Environment
==================================================

This is a DELIBERATELY VULNERABLE web application for training the AI agent.
It includes ALL OWASP Top 10 2025 vulnerabilities.

⚠️  WARNING: NEVER deploy this in production! For training only!
"""

from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify, make_response
import sqlite3
import pickle
import base64
import hashlib
import jwt
import os
import time
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
app.secret_key = 'insecure_secret_key_12345'  # A02: Security Misconfiguration

# Setup logging (for A09 testing)
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize database
def init_db():
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, 
                  role TEXT, balance REAL, email TEXT)''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, 
                  quantity INTEGER, total REAL, timestamp TEXT)''')
    
    # Insert test data
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin', 'admin', 10000.0, 'admin@test.com')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'password', 'user', 100.0, 'user@test.com')")
    c.execute("INSERT OR IGNORE INTO products VALUES (1, 'Premium Item', 999.99, 10)")
    c.execute("INSERT OR IGNORE INTO products VALUES (2, 'Regular Item', 9.99, 100)")
    
    conn.commit()
    conn.close()

init_db()

# ============================================================================
# A01: Broken Access Control
# ============================================================================

@app.route('/profile')
def profile():
    """IDOR vulnerability - can access any user's profile"""
    user_id = request.args.get('uid', '1')
    
    # Vulnerable: No authorization check!
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE id = {user_id}")  # Also SQLi!
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'role': user[3],
            'balance': user[4],
            'email': user[5]
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/users')
def admin_users():
    """Missing access control - anyone can access"""
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, balance FROM users")
    users = c.fetchall()
    conn.close()
    
    return jsonify({'users': users})

# ============================================================================
# A02: Security Misconfiguration
# ============================================================================

@app.route('/debug')
def debug():
    """Debug mode exposed in production"""
    return jsonify({
        'debug': True,
        'secret_key': app.secret_key,
        'database': 'training.db',
        'python_version': '3.13'
    })

@app.route('/config')
def config():
    """Exposed configuration"""
    return jsonify({
        'database_url': 'sqlite:///training.db',
        'api_keys': {
            'aws': 'AKIAIOSFODNN7EXAMPLE',
            'stripe': 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'
        }
    })

# ============================================================================
# A03: Software Supply Chain Failures
# ============================================================================

@app.route('/install_package', methods=['POST'])
def install_package():
    """Vulnerable package installation"""
    package_name = request.json.get('package')
    
    # Vulnerable: No validation of package source!
    # Simulates typosquatting vulnerability
    if 'reqeusts' in package_name:  # Typo of 'requests'
        return jsonify({'status': 'Malicious package detected!', 'vulnerability': 'A03'}), 200
    
    return jsonify({'status': 'Package installed'})

# ============================================================================
# A04: Cryptographic Failures
# ============================================================================

@app.route('/weak_crypto')
def weak_crypto():
    """Uses weak cryptography"""
    data = request.args.get('data', 'test')
    
    # Vulnerable: MD5 is broken!
    weak_hash = hashlib.md5(data.encode()).hexdigest()
    
    return jsonify({
        'hash': weak_hash,
        'algorithm': 'MD5',
        'vulnerability': 'A04 - Weak hashing'
    })

@app.route('/get_token')
def get_token():
    """Issues JWT with 'none' algorithm vulnerability"""
    username = request.args.get('user', 'guest')
    
    # Vulnerable: Accepts 'none' algorithm
    token = jwt.encode({'user': username, 'role': 'user'}, '', algorithm='none')
    
    return jsonify({'token': token})

# ============================================================================
# A05: Injection
# ============================================================================

@app.route('/search')
def search():
    """SQL Injection vulnerability"""
    query = request.args.get('q', '')
    
    # Vulnerable: Direct SQL injection!
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'")
        results = c.fetchall()
        conn.close()
        return jsonify({'results': results})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/comment', methods=['POST'])
def comment():
    """XSS vulnerability"""
    comment_text = request.json.get('comment', '')
    
    # Vulnerable: No sanitization!
    html = f"""
    <html>
    <body>
        <h1>Your Comment:</h1>
        <div>{comment_text}</div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/template')
def template():
    """SSTI (Server-Side Template Injection)"""
    name = request.args.get('name', 'Guest')
    
    # Vulnerable: Direct template rendering!
    template = f"<h1>Hello {{{{{name}}}}}</h1>"
    return render_template_string(template)

@app.route('/ping', methods=['POST'])
def ping():
    """Command Injection"""
    host = request.json.get('host', 'localhost')
    
    # Vulnerable: Command injection!
    import subprocess
    try:
        result = subprocess.check_output(f'ping -c 1 {host}', shell=True)
        return jsonify({'result': result.decode()})
    except:
        return jsonify({'error': 'Command failed'}), 500

# ============================================================================
# A06: Insecure Design
# ============================================================================

@app.route('/purchase', methods=['POST'])
def purchase():
    """Business logic flaw - negative quantities allowed"""
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))  # Can be negative!
    
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    c.execute(f"SELECT price FROM products WHERE id = {product_id}")
    product = c.fetchone()
    
    if product:
        price = product[0]
        total = price * quantity  # Negative total if quantity is negative!
        
        # Vulnerable: No validation of quantity or total!
        c.execute(f"INSERT INTO orders VALUES (NULL, 1, {product_id}, {quantity}, {total}, '{datetime.now()}')")
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'Order placed',
            'total': total,
            'vulnerability': 'A06 - Business Logic Flaw'
        })
    
    conn.close()
    return jsonify({'error': 'Product not found'}), 404

@app.route('/race_condition', methods=['POST'])
def race_condition():
    """Race condition vulnerability"""
    user_id = request.json.get('user_id', 1)
    amount = float(request.json.get('amount', 10))
    
    # Vulnerable: No locking mechanism!
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    
    # Check balance
    c.execute(f"SELECT balance FROM users WHERE id = {user_id}")
    balance = c.fetchone()[0]
    
    # Simulate delay (race condition window)
    time.sleep(0.1)
    
    # Deduct amount
    if balance >= amount:
        new_balance = balance - amount
        c.execute(f"UPDATE users SET balance = {new_balance} WHERE id = {user_id}")
        conn.commit()
        conn.close()
        return jsonify({'status': 'Success', 'new_balance': new_balance})
    
    conn.close()
    return jsonify({'error': 'Insufficient funds'}), 400

# ============================================================================
# A07: Identification and Authentication Failures
# ============================================================================

@app.route('/login', methods=['POST'])
def login():
    """SQL injection in authentication"""
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    
    # Vulnerable: SQL injection in login!
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    c.execute(query)
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        return jsonify({'status': 'Login successful', 'role': user[3]})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/reset_password', methods=['POST'])
def reset_password():
    """Weak password reset"""
    email = request.json.get('email', '')
    
    # Vulnerable: Predictable reset token!
    reset_token = hashlib.md5(email.encode()).hexdigest()
    
    return jsonify({
        'reset_token': reset_token,
        'vulnerability': 'A07 - Predictable token'
    })

# ============================================================================
# A08: Data Integrity Failures
# ============================================================================

@app.route('/deserialize', methods=['POST'])
def deserialize():
    """Insecure deserialization"""
    data = request.json.get('data', '')
    
    try:
        # Vulnerable: Unsafe deserialization!
        decoded = base64.b64decode(data)
        obj = pickle.loads(decoded)
        return jsonify({'result': str(obj), 'vulnerability': 'A08'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# A09: Security Logging Failures
# ============================================================================

@app.route('/log_action', methods=['POST'])
def log_action():
    """Log injection vulnerability"""
    action = request.json.get('action', '')
    
    # Vulnerable: No sanitization of log input!
    logging.info(f"User action: {action}")
    
    return jsonify({'status': 'Logged', 'vulnerability': 'A09 - Log Injection'})

# ============================================================================
# A10: Mishandling of Exceptional Conditions
# ============================================================================

@app.route('/divide')
def divide():
    """Error disclosure"""
    try:
        a = int(request.args.get('a', 10))
        b = int(request.args.get('b', 0))
        result = a / b
        return jsonify({'result': result})
    except Exception as e:
        # Vulnerable: Exposes full error details!
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'traceback': 'Full stack trace would be here',
            'vulnerability': 'A10'
        }), 500

# ============================================================================
# Home Page
# ============================================================================

@app.route('/')
def home():
    return """
    <html>
    <head><title>OWASP Top 10 2025 Training Environment</title></head>
    <body>
        <h1>🎯 OWASP Top 10 2025 - Complete Training Environment</h1>
        <p>This application contains ALL OWASP Top 10 2025 vulnerabilities for AI training.</p>
        
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/profile?uid=1">A01: Broken Access Control (IDOR)</a></li>
            <li><a href="/admin/users">A01: Missing Access Control</a></li>
            <li><a href="/debug">A02: Debug Mode Exposed</a></li>
            <li><a href="/config">A02: Config Exposed</a></li>
            <li><a href="/weak_crypto?data=test">A04: Weak Cryptography</a></li>
            <li><a href="/search?q=test">A05: SQL Injection</a></li>
            <li><a href="/template?name=test">A05: SSTI</a></li>
            <li><a href="/divide?a=10&b=0">A10: Error Disclosure</a></li>
        </ul>
        
        <h2>Modern API Endpoints (2025):</h2>
        <ul>
            <li><a href="/api/v1/users">REST API - Users</a></li>
            <li><a href="/api/v1/products">REST API - Products</a></li>
            <li><a href="/api/v2/auth/token">OAuth 2.0 Token</a></li>
            <li><a href="/graphql">GraphQL Endpoint</a></li>
            <li><a href="/api/health">Health Check</a></li>
            <li><a href="/api/metrics">Prometheus Metrics</a></li>
            <li><a href="/swagger">Swagger/OpenAPI Docs</a></li>
        </ul>
        
        <h2>POST Endpoints:</h2>
        <ul>
            <li>POST /login - A07: Auth Bypass</li>
            <li>POST /comment - A05: XSS</li>
            <li>POST /ping - A05: Command Injection</li>
            <li>POST /purchase - A06: Business Logic</li>
            <li>POST /race_condition - A06: Race Condition</li>
            <li>POST /deserialize - A08: Insecure Deserialization</li>
            <li>POST /log_action - A09: Log Injection</li>
            <li>POST /api/v1/users - REST API Create</li>
            <li>POST /graphql - GraphQL Query</li>
        </ul>
        
        <p><strong>⚠️ WARNING: This is DELIBERATELY VULNERABLE! For training only!</strong></p>
    </body>
    </html>
    """

# ============================================================================
# Modern 2025 API Endpoints
# ============================================================================

# REST API v1 - Standard CRUD operations
@app.route('/api/v1/users', methods=['GET'])
def api_v1_users_list():
    """REST API - List users (vulnerable to injection)"""
    limit = request.args.get('limit', '10')
    offset = request.args.get('offset', '0')
    
    # Vulnerable: SQL injection in pagination
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    query = f"SELECT id, username, email, role FROM users LIMIT {limit} OFFSET {offset}"
    c.execute(query)
    users = c.fetchall()
    conn.close()
    
    return jsonify({
        'data': [{'id': u[0], 'username': u[1], 'email': u[2], 'role': u[3]} for u in users],
        'meta': {'limit': limit, 'offset': offset}
    })

@app.route('/api/v1/users/<user_id>', methods=['GET'])
def api_v1_user_detail(user_id):
    """REST API - Get user detail (IDOR vulnerability)"""
    # Vulnerable: No authorization check
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[5],
            'role': user[3],
            'balance': user[4]
        })
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/v1/users', methods=['POST'])
def api_v1_create_user():
    """REST API - Create user (mass assignment vulnerability)"""
    data = request.json
    
    # Vulnerable: Mass assignment - can set any field including 'role'!
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')  # Should not be user-controllable!
    balance = data.get('balance', 0)  # Should not be user-controllable!
    
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    c.execute(f"INSERT INTO users VALUES (NULL, '{username}', '{password}', '{role}', {balance}, '{email}')")
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    
    return jsonify({
        'id': user_id,
        'username': username,
        'role': role,
        'vulnerability': 'Mass Assignment - can create admin users!'
    }), 201

@app.route('/api/v1/users/<user_id>', methods=['PUT', 'PATCH'])
def api_v1_update_user(user_id):
    """REST API - Update user (IDOR + Mass Assignment)"""
    data = request.json
    
    # Vulnerable: No authorization + mass assignment
    updates = []
    for key, value in data.items():
        if key in ['username', 'email', 'role', 'balance']:  # All fields modifiable!
            updates.append(f"{key} = '{value}'")
    
    if updates:
        conn = sqlite3.connect('training.db')
        c = conn.cursor()
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = {user_id}"
        c.execute(query)
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'Updated', 'vulnerability': 'IDOR + Mass Assignment'})
    
    return jsonify({'error': 'No fields to update'}), 400

@app.route('/api/v1/users/<user_id>', methods=['DELETE'])
def api_v1_delete_user(user_id):
    """REST API - Delete user (missing authorization)"""
    # Vulnerable: Anyone can delete any user!
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'Deleted', 'vulnerability': 'Missing Authorization'}), 200

# REST API v2 - OAuth/JWT endpoints
@app.route('/api/v2/auth/token', methods=['POST'])
def api_v2_get_token():
    """OAuth 2.0 style token endpoint (vulnerable)"""
    grant_type = request.json.get('grant_type')
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Vulnerable: Weak JWT with predictable secret
    token = jwt.encode({
        'sub': username,
        'role': 'user',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, 'weak_secret_123', algorithm='HS256')
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 86400,
        'vulnerability': 'Weak JWT secret'
    })

@app.route('/api/v2/auth/refresh', methods=['POST'])
def api_v2_refresh_token():
    """Refresh token endpoint (vulnerable to token reuse)"""
    refresh_token = request.json.get('refresh_token')
    
    # Vulnerable: No token rotation, same token works forever
    new_token = jwt.encode({
        'sub': 'user',
        'role': 'user',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, 'weak_secret_123', algorithm='HS256')
    
    return jsonify({
        'access_token': new_token,
        'vulnerability': 'No token rotation'
    })

# GraphQL Endpoint
@app.route('/graphql', methods=['GET', 'POST'])
def graphql_endpoint():
    """GraphQL endpoint (vulnerable to injection)"""
    if request.method == 'GET':
        return jsonify({
            'message': 'GraphQL endpoint',
            'example': 'POST {"query": "{ user(id: 1) { username email } }"}'
        })
    
    query = request.json.get('query', '')
    
    # Vulnerable: GraphQL injection
    if 'user' in query:
        # Extract ID from query (very naive parsing)
        import re
        match = re.search(r'id:\s*(\d+|"[^"]*")', query)
        if match:
            user_id = match.group(1).strip('"')
            
            conn = sqlite3.connect('training.db')
            c = conn.cursor()
            # Vulnerable: SQL injection via GraphQL
            c.execute(f"SELECT * FROM users WHERE id = {user_id}")
            user = c.fetchone()
            conn.close()
            
            if user:
                return jsonify({
                    'data': {
                        'user': {
                            'id': user[0],
                            'username': user[1],
                            'email': user[5],
                            'role': user[3]
                        }
                    },
                    'vulnerability': 'GraphQL Injection'
                })
    
    return jsonify({'data': None})

# Microservices patterns
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint (leaks internal info)"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'database': 'connected',
        'internal_ip': '192.168.1.100',  # Vulnerable: Info disclosure
        'debug_mode': True,
        'vulnerability': 'Information Disclosure'
    })

@app.route('/api/metrics', methods=['GET'])
def metrics():
    """Prometheus-style metrics (exposes sensitive data)"""
    return """
    # HELP app_requests_total Total requests
    app_requests_total{endpoint="/admin"} 1523
    app_requests_total{endpoint="/api/v1/users"} 8234
    
    # HELP app_errors_total Total errors
    app_errors_total{type="sql_injection"} 42
    app_errors_total{type="auth_failure"} 156
    
    # HELP app_secrets Exposed secrets
    app_database_password="super_secret_pass"
    app_api_key="sk_live_51234567890"
    """

@app.route('/swagger', methods=['GET'])
def swagger_docs():
    """Swagger/OpenAPI documentation (exposes all endpoints)"""
    return jsonify({
        'openapi': '3.0.0',
        'info': {'title': 'Vulnerable API', 'version': '1.0.0'},
        'paths': {
            '/api/v1/users': {
                'get': {'summary': 'List users', 'vulnerable': True},
                'post': {'summary': 'Create user', 'vulnerable': 'Mass Assignment'}
            },
            '/admin/users': {
                'get': {'summary': 'Admin only', 'vulnerable': 'Missing Auth'}
            }
        },
        'vulnerability': 'Full API disclosure'
    })

# WebSocket-style endpoint (simulated)
@app.route('/ws/notifications', methods=['GET'])
def websocket_notifications():
    """WebSocket endpoint (CORS vulnerability)"""
    origin = request.headers.get('Origin', '*')
    
    response = make_response(jsonify({
        'type': 'notification',
        'message': 'Real-time updates',
        'vulnerability': 'CORS misconfiguration'
    }))
    
    # Vulnerable: Allows any origin!
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

# File upload endpoint
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload (unrestricted file upload vulnerability)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    filename = file.filename
    
    # Vulnerable: No file type validation, no size limit!
    file.save(f'uploads/{filename}')
    
    return jsonify({
        'filename': filename,
        'path': f'/uploads/{filename}',
        'vulnerability': 'Unrestricted File Upload'
    })

# Rate limiting bypass
@app.route('/api/sensitive', methods=['GET'])
def sensitive_endpoint():
    """Endpoint that should be rate-limited but isn't"""
    # Vulnerable: No rate limiting!
    return jsonify({
        'sensitive_data': 'This should be rate-limited',
        'vulnerability': 'Missing Rate Limiting'
    })

# ============================================================================
# File Inclusion Vulnerabilities
# ============================================================================

@app.route('/read_file')
def read_file():
    """Local File Inclusion (LFI) vulnerability"""
    filename = request.args.get('file', 'welcome.txt')
    
    # Vulnerable: Direct file inclusion!
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return jsonify({
            'file': filename,
            'content': content,
            'vulnerability': 'LFI - Can read /etc/passwd, C:\\Windows\\System32\\config\\SAM'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/include_page')
def include_page():
    """Remote File Inclusion (RFI) vulnerability"""
    page = request.args.get('page', 'home')
    
    # Vulnerable: Can include remote files!
    try:
        if page.startswith('http'):
            import urllib.request
            with urllib.request.urlopen(page) as response:
                content = response.read().decode()
            return render_template_string(content)
        else:
            with open(f'pages/{page}.html', 'r') as f:
                content = f.read()
            return render_template_string(content)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'vulnerability': 'RFI - Can include http://attacker.com/shell.php'
        }), 500

@app.route('/download')
def download_file():
    """Path Traversal vulnerability"""
    filename = request.args.get('file', 'document.pdf')
    
    # Vulnerable: No path sanitization!
    filepath = f'downloads/{filename}'
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        return content
    except Exception as e:
        return jsonify({
            'error': str(e),
            'vulnerability': 'Path Traversal - Try: ../../etc/passwd'
        }), 500

# ============================================================================
# XXE (XML External Entity) Injection
# ============================================================================

@app.route('/parse_xml', methods=['POST'])
def parse_xml():
    """XXE vulnerability"""
    xml_data = request.data.decode()
    
    # Vulnerable: Unsafe XML parsing!
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_data)
        
        return jsonify({
            'parsed': ET.tostring(root).decode(),
            'vulnerability': 'XXE - Can read local files via <!ENTITY>'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CSRF (Cross-Site Request Forgery)
# ============================================================================

@app.route('/transfer_money', methods=['POST'])
def transfer_money():
    """CSRF vulnerability - no token validation"""
    to_user = request.form.get('to_user') or request.json.get('to_user')
    amount = request.form.get('amount') or request.json.get('amount')
    
    # Vulnerable: No CSRF token validation!
    return jsonify({
        'status': 'Transfer completed',
        'to': to_user,
        'amount': amount,
        'vulnerability': 'CSRF - No token validation'
    })

@app.route('/change_email', methods=['POST'])
def change_email():
    """CSRF vulnerability"""
    new_email = request.form.get('email') or request.json.get('email')
    
    # Vulnerable: No CSRF protection!
    return jsonify({
        'status': 'Email changed',
        'new_email': new_email,
        'vulnerability': 'CSRF'
    })

# ============================================================================
# Clickjacking
# ============================================================================

@app.route('/sensitive_action')
def sensitive_action():
    """Clickjacking vulnerability - missing X-Frame-Options"""
    html = """
    <html>
    <body>
        <h1>Sensitive Action Page</h1>
        <button onclick="alert('Action performed!')">Delete Account</button>
        <p>This page can be framed by attackers!</p>
    </body>
    </html>
    """
    response = make_response(html)
    # Vulnerable: No X-Frame-Options header!
    return response

# ============================================================================
# Open Redirect
# ============================================================================

@app.route('/redirect')
def open_redirect():
    """Open redirect vulnerability"""
    url = request.args.get('url', '/')
    
    # Vulnerable: No URL validation!
    return redirect(url)

@app.route('/oauth_callback')
def oauth_callback():
    """OAuth open redirect"""
    redirect_uri = request.args.get('redirect_uri', '/')
    
    # Vulnerable: Unvalidated redirect_uri
    return redirect(redirect_uri)

# ============================================================================
# SSRF (Server-Side Request Forgery)
# ============================================================================

@app.route('/fetch_url', methods=['POST'])
def fetch_url():
    """SSRF vulnerability"""
    url = request.json.get('url')
    
    # Vulnerable: Can access internal resources!
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response:
            content = response.read().decode()
        return jsonify({
            'content': content[:500],
            'vulnerability': 'SSRF - Can access http://169.254.169.254/latest/meta-data/'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """SSRF via webhook"""
    callback_url = request.json.get('callback_url')
    
    # Vulnerable: Unvalidated callback URL
    try:
        import urllib.request
        urllib.request.urlopen(callback_url)
        return jsonify({'status': 'Webhook sent', 'vulnerability': 'SSRF'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# LDAP Injection
# ============================================================================

@app.route('/ldap_search')
def ldap_search():
    """LDAP injection vulnerability"""
    username = request.args.get('username', '')
    
    # Vulnerable: LDAP injection
    ldap_query = f"(&(objectClass=user)(uid={username}))"
    
    return jsonify({
        'query': ldap_query,
        'vulnerability': 'LDAP Injection - Try: *)(uid=*))(|(uid=*'
    })

# ============================================================================
# NoSQL Injection
# ============================================================================

@app.route('/nosql_login', methods=['POST'])
def nosql_login():
    """NoSQL injection (MongoDB style)"""
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Vulnerable: NoSQL injection
    # In real MongoDB: db.users.find({username: username, password: password})
    # Attack: {"username": {"$ne": null}, "password": {"$ne": null}}
    
    if isinstance(username, dict) or isinstance(password, dict):
        return jsonify({
            'status': 'Login successful',
            'vulnerability': 'NoSQL Injection - Bypassed with $ne operator'
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# ============================================================================
# Host Header Injection
# ============================================================================

@app.route('/reset_link')
def reset_link():
    """Host header injection"""
    host = request.headers.get('Host', 'localhost:5000')
    
    # Vulnerable: Uses untrusted Host header
    reset_url = f"http://{host}/reset?token=abc123"
    
    return jsonify({
        'reset_url': reset_url,
        'vulnerability': 'Host Header Injection - Can poison password reset links'
    })

# ============================================================================
# HTTP Response Splitting
# ============================================================================

@app.route('/set_language')
def set_language():
    """HTTP response splitting"""
    lang = request.args.get('lang', 'en')
    
    # Vulnerable: CRLF injection in headers
    response = make_response(jsonify({'language': lang}))
    response.headers['X-Language'] = lang  # Can inject \r\n
    
    return response

# ============================================================================
# Insecure Direct Object Reference (IDOR) - Additional Examples
# ============================================================================

@app.route('/invoice/<invoice_id>')
def view_invoice(invoice_id):
    """IDOR - View any invoice"""
    # Vulnerable: No ownership check
    return jsonify({
        'invoice_id': invoice_id,
        'amount': 1000.00,
        'customer': 'John Doe',
        'vulnerability': 'IDOR - Can view any invoice'
    })

@app.route('/api/documents/<doc_id>')
def get_document(doc_id):
    """IDOR - Access any document"""
    # Vulnerable: No authorization
    return jsonify({
        'document_id': doc_id,
        'title': 'Confidential Document',
        'content': 'Secret information',
        'vulnerability': 'IDOR'
    })

# ============================================================================
# Mass Assignment
# ============================================================================

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Mass assignment vulnerability"""
    data = request.json
    
    # Vulnerable: Accepts all fields including 'is_admin'
    user_data = {
        'username': data.get('username'),
        'email': data.get('email'),
        'is_admin': data.get('is_admin', False),  # Should not be user-controllable!
        'credit_balance': data.get('credit_balance', 0)  # Should not be user-controllable!
    }
    
    return jsonify({
        'updated': user_data,
        'vulnerability': 'Mass Assignment - Can set is_admin=true'
    })

# ============================================================================
# Prototype Pollution (JavaScript/Node.js style)
# ============================================================================

@app.route('/merge_config', methods=['POST'])
def merge_config():
    """Prototype pollution vulnerability"""
    user_config = request.json
    
    # Vulnerable: Deep merge without sanitization
    # In JavaScript: Object.assign({}, defaultConfig, userConfig)
    # Attack: {"__proto__": {"isAdmin": true}}
    
    if '__proto__' in str(user_config):
        return jsonify({
            'status': 'Config merged',
            'vulnerability': 'Prototype Pollution - Can pollute Object.prototype'
        })
    
    return jsonify({'status': 'Config merged'})

# ============================================================================
# Timing Attack
# ============================================================================

@app.route('/check_username', methods=['POST'])
def check_username():
    """Timing attack vulnerability"""
    username = request.json.get('username', '')
    
    # Vulnerable: Different response times reveal if username exists
    import time
    
    valid_usernames = ['admin', 'user', 'test']
    
    if username in valid_usernames:
        time.sleep(0.5)  # Simulates database lookup
        return jsonify({'exists': True})
    
    return jsonify({'exists': False})

# ============================================================================
# Information Disclosure
# ============================================================================

@app.route('/server_info')
def server_info():
    """Information disclosure"""
    import platform
    import sys
    
    return jsonify({
        'python_version': sys.version,
        'platform': platform.platform(),
        'hostname': platform.node(),
        'database': 'PostgreSQL 14.2',
        'internal_ip': '192.168.1.100',
        'api_keys': {
            'stripe': 'sk_live_xxxxx',
            'aws': 'AKIA...'
        },
        'vulnerability': 'Information Disclosure'
    })

@app.route('/.git/config')
def git_config():
    """Exposed .git directory"""
    return """
    [core]
        repositoryformatversion = 0
    [remote "origin"]
        url = https://github.com/company/secret-repo.git
    [user]
        email = admin@company.com
    """, 200, {'Content-Type': 'text/plain'}

# ============================================================================
# Insecure Randomness
# ============================================================================

@app.route('/generate_token')
def generate_token():
    """Predictable token generation"""
    import random
    
    # Vulnerable: Using weak random
    token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    return jsonify({
        'token': token,
        'vulnerability': 'Weak Random - Predictable tokens'
    })

# ============================================================================
# Session Fixation
# ============================================================================

@app.route('/set_session')
def set_session():
    """Session fixation vulnerability"""
    session_id = request.args.get('session_id')
    
    if session_id:
        # Vulnerable: Accepts user-provided session ID
        session['id'] = session_id
        return jsonify({
            'status': 'Session set',
            'session_id': session_id,
            'vulnerability': 'Session Fixation'
        })
    
    return jsonify({'error': 'No session_id provided'}), 400

if __name__ == '__main__':
    print("=" * 70)
    print("🎯 OWASP Top 10 2025 Training Environment")
    print("=" * 70)
    print("⚠️  This application is DELIBERATELY VULNERABLE!")
    print("   For AI training purposes ONLY!")
    print("   NEVER deploy in production!")
    print("=" * 70)
    print("\n🚀 Starting server on http://localhost:5000")
    print("   Use this URL to train your AI agent\n")
    print("📋 Total Endpoints: 50+")
    print("🎯 Vulnerability Types: 25+")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
