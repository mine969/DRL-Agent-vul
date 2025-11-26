"""
🚀 MODERNHUB PLATFORM 2025 - AI Security Training Environment
==============================================================

A realistic, modern web application combining:
- Social Media (posts, likes, messages)
- E-commerce (products, cart, payments)
- SaaS Features (subscriptions, API keys)
- All OWASP Top 10 2025 vulnerabilities

⚠️ DELIBERATELY VULNERABLE - For AI Training Only!
"""

from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, make_response, render_template_string, send_from_directory
import sqlite3
import jwt
import datetime
import hashlib
import os
import random
import string
import time
import pickle
import base64
from functools import wraps

app = Flask(__name__)
app.secret_key = 'modern_platform_2025_secret'
JWT_SECRET = 'jwt_secret_2025'
DB_NAME = 'modern_platform.db'

# ============================================================================
# DATABASE SETUP - Modern 2025 Schema
# ============================================================================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Enhanced Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        bio TEXT,
        avatar_url TEXT,
        verified BOOLEAN DEFAULT 0,
        subscription_tier TEXT DEFAULT 'free',
        api_key TEXT,
        balance REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Posts table (social media)
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        content TEXT,
        image_url TEXT,
        likes INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Comments table
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        content TEXT,
        author_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Products table (e-commerce)
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        stock INTEGER,
        category TEXT,
        image_url TEXT,
        seller_id INTEGER,
        FOREIGN KEY(seller_id) REFERENCES users(id)
    )''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    
    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        content TEXT,
        read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(from_user_id) REFERENCES users(id),
        FOREIGN KEY(to_user_id) REFERENCES users(id)
    )''')
    
    # Seed data
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        print("🌱 Seeding modern platform database...")
        
        # Create users with modern data
        users = [
            ('admin', 'admin@modernhub.com', 'secure_password_123', 'admin', 'Platform Administrator 👑', 
             'https://i.pravatar.cc/150?img=1', 1, 'premium', 'sk_live_admin_key_123', 10000.0),
            ('alice', 'alice@example.com', 'password', 'user', 'Tech enthusiast & AI researcher 🚀', 
             'https://i.pravatar.cc/150?img=2', 1, 'pro', 'sk_live_alice_key_456', 500.0),
            ('bob', 'bob@example.com', 'password', 'user', 'Full-stack developer 💻', 
             'https://i.pravatar.cc/150?img=3', 0, 'free', 'sk_test_bob_key_789', 50.0),
            ('seller', 'seller@shop.com', 'password', 'seller', 'Official Store 🏪', 
             'https://i.pravatar.cc/150?img=4', 1, 'business', 'sk_live_seller_key_999', 5000.0)
        ]
        
        for user in users:
            c.execute("""INSERT INTO users (username, email, password, role, bio, avatar_url, verified, 
                        subscription_tier, api_key, balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", user)
        
        # Create posts
        posts = [
            (1, 'Welcome to ModernHub!', 'Excited to launch our new platform! 🎉 #launch', 
             'https://picsum.photos/600/400?random=1', 42, 12),
            (2, 'AI Project Launch', 'Just deployed my new AI security scanner! 🤖 Check it out!', 
             'https://picsum.photos/600/400?random=2', 28, 5),
            (3, 'Beautiful Day', 'Amazing sunset today 🌅 #photography', 
             'https://picsum.photos/600/400?random=3', 156, 23),
            (4, 'New Products!', 'Check out our latest products in the store! 🛍️ #shopping', 
             'https://picsum.photos/600/400?random=4', 89, 15)
        ]
        
        for post in posts:
            c.execute("INSERT INTO posts (user_id, title, content, image_url, likes, shares) VALUES (?, ?, ?, ?, ?, ?)", post)
        
        # Create products
        products = [
            ('Premium AI Course', 'Master AI & Machine Learning in 2025', 299.99, 50, 'Education', 
             'https://picsum.photos/300/300?random=5', 4),
            ('Smart Watch Pro', 'Latest smartwatch with AI features', 399.99, 100, 'Electronics', 
             'https://picsum.photos/300/300?random=6', 4),
            ('Coding Bootcamp', 'Full-stack development masterclass', 499.99, 30, 'Education', 
             'https://picsum.photos/300/300?random=7', 4),
            ('Designer Headphones', 'Premium audio experience', 199.99, 75, 'Electronics', 
             'https://picsum.photos/300/300?random=8', 4)
        ]
        
        for product in products:
            c.execute("""INSERT INTO products (name, description, price, stock, category, image_url, seller_id) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", product)
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        elif 'secure_sess_id_v2' in request.cookies:
            token = request.cookies['secure_sess_id_v2']
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            conn = get_db_connection()
            current_user = conn.execute('SELECT * FROM users WHERE username = ?', (data['user'],)).fetchone()
            conn.close()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# --- API ROUTES (CTF Mode: Obscured Endpoints) ---

@app.route('/api/v1/auth/gate_keeper_99', methods=['POST'])
def api_login():
    # CTF Hint: "The gate keeper only lets the admin pass."
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Gate closed'}), 401
    
    conn = get_db_connection()
    
    # VULNERABILITY: SQL Injection (Classic)
    query = f"SELECT * FROM users WHERE username = '{auth['username']}' AND password = '{auth['password']}'"
    try:
        user = conn.execute(query).fetchone()
    except Exception as e:
        return jsonify({'message': 'DB_ERR_X99', 'error': str(e)}), 500
    finally:
        conn.close()
        
    if user:
        token = jwt.encode({
            'user': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'flag': 'CTF{JWT_MASTER_KEY_FOUND}' # Hidden flag in token
        }, JWT_SECRET, algorithm="HS256")
        
        return jsonify({'auth_token_v2': token, 'access_level': user['role']})
    
    return jsonify({'message': 'Access Denied'}), 401

@app.route('/api/v1/content/stream_77', methods=['GET'])
def get_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in posts])

@app.route('/api/v1/interact/comment_x', methods=['POST'])
@token_required
def api_add_comment(current_user):
    data = request.json
    content = data.get('payload') # Changed from 'content' to 'payload'
    post_id = data.get('target_id') # Changed from 'post_id' in URL
    
    # VULNERABILITY: Stored XSS
    conn = get_db_connection()
    conn.execute('INSERT INTO comments (post_id, content, author_name) VALUES (?, ?, ?)',
                 (post_id, content, current_user['username']))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'payload_accepted', 'flag_hint': 'check_the_logs'})

@app.route('/api/internal/sys_admin/users_db_dump', methods=['GET'])
@token_required
def api_admin_users(current_user):
    # VULNERABILITY: Broken Access Control
    # CTF Flag hidden in response
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role, "CTF{DB_LEAK_SUCCESS}" as flag FROM users').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in users])

# --- FRONTEND ROUTES (Hybrid) ---

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    response = make_response(render_template('blog_index.html', posts=posts))
    response.headers['X-CTF-Hint'] = 'try_api_v1_auth_gate_keeper_99'
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            user = conn.execute(query).fetchone()
        except:
            user = None
        conn.close()
            
        if user:
            token = jwt.encode({
                'user': user['username'],
                'role': user['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, JWT_SECRET, algorithm="HS256")
            
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('secure_sess_id_v2', token) # Obscure cookie name
            session['user'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return resp
        
        flash("Invalid credentials", "danger")
    
    return render_template('blog_login.html', csrf_token="jwt_mode_no_csrf")

@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,)).fetchall()
    conn.close()
    
    if not post:
        return "Post not found", 404
        
    return render_template('blog_post.html', post=post, comments=comments, csrf_token="jwt_mode")

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULNERABILITY: Reflected XSS
    return render_template('blog_search.html', query=query)

@app.route('/profile')
def profile():
    token = request.cookies.get('secure_sess_id_v2') # Changed cookie name
    if not token:
        return redirect(url_for('login'))
        
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return redirect(url_for('login'))

    # VULNERABILITY: IDOR
    user_id = request.args.get('uid') # Changed param from user_id to uid
    conn = get_db_connection()
    
    if user_id:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return f"Profile: {user['username']} | Role: {user['role']} | ID: {user['id']} | Flag: CTF{{IDOR_MASTER}}"
            
    return f"Profile: {data['user']} | Role: {data['role']}"

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('secure_sess_id_v2', '', expires=0)
    session.clear()
    return resp

# ============================================================================
# OWASP Top 10 2025 - Additional Endpoints
# ============================================================================

# File Inclusion Vulnerabilities
@app.route('/read_file')
def read_file():
    """LFI vulnerability"""
    filename = request.args.get('file', 'welcome.txt')
    try:
        with open(filename, 'r') as f:
            return jsonify({'file': filename, 'content': f.read(), 'vuln': 'LFI'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download_file():
    """Path Traversal"""
    filename = request.args.get('file', 'document.pdf')
    try:
        with open(f'downloads/{filename}', 'rb') as f:
            return f.read()
    except Exception as e:
        return jsonify({'error': str(e), 'vuln': 'Path Traversal'}), 500

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Unrestricted File Upload Vulnerability"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # VULNERABILITY: No validation of file extension or content
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        
        return jsonify({
            'message': f'File {file.filename} uploaded successfully!', 
            'path': f'/uploads/{file.filename}',
            'vuln': 'Unrestricted File Upload'
        })
        
    return render_template_string('''
        <h1>Upload File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
    ''')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# REST API Endpoints
@app.route('/api/v1/users', methods=['GET', 'POST'])
def api_users():
    """REST API with SQLi and Mass Assignment"""
    if request.method == 'GET':
        limit = request.args.get('limit', '10')
        conn = get_db_connection()
        # VULN: SQL Injection in pagination
        users = conn.execute(f"SELECT id, username, role FROM users LIMIT {limit}").fetchall()
        return jsonify({'data': [dict(u) for u in users]})
    else:
        data = request.json
        # VULN: Mass Assignment - can set role!
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (data.get('username'), data.get('password'), data.get('role', 'user')))
        conn.commit()
        return jsonify({'status': 'created', 'vuln': 'Mass Assignment'}), 201

@app.route('/api/v1/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def api_user_detail(user_id):
    """REST API IDOR"""
    conn = get_db_connection()
    if request.method == 'GET':
        # VULN: IDOR - no auth check
        user = conn.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
        return jsonify(dict(user)) if user else ('', 404)
    elif request.method == 'PUT':
        # VULN: IDOR + Mass Assignment
        data = request.json
        conn.execute(f"UPDATE users SET username=?, role=? WHERE id={user_id}",
                    (data.get('username'), data.get('role')))
        conn.commit()
        return jsonify({'status': 'updated', 'vuln': 'IDOR+Mass Assignment'})
    else:  # DELETE
        # VULN: Missing authorization
        conn.execute(f"DELETE FROM users WHERE id = {user_id}")
        conn.commit()
        return jsonify({'status': 'deleted', 'vuln': 'Missing Auth'})

# GraphQL Endpoint
@app.route('/graphql', methods=['GET', 'POST'])
def graphql():
    """GraphQL with injection"""
    if request.method == 'GET':
        return jsonify({'info': 'GraphQL endpoint', 'example': '{"query": "{ user(id: 1) { username } }"}'})
    
    query = request.json.get('query', '')
    # VULN: GraphQL injection
    import re
    match = re.search(r'id:\s*(\d+)', query)
    if match:
        user_id = match.group(1)
        conn = get_db_connection()
        user = conn.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
        return jsonify({'data': {'user': dict(user) if user else None}, 'vuln': 'GraphQL Injection'})
    return jsonify({'data': None})

# OAuth/JWT Endpoints
@app.route('/api/v2/auth/token', methods=['POST'])
def get_token():
    """Weak JWT"""
    data = request.json
    token = jwt.encode({'user': data.get('username'), 'role': 'user'}, 
                      'weak_secret_123', algorithm='HS256')
    return jsonify({'access_token': token, 'vuln': 'Weak JWT Secret'})

# Microservices Patterns
@app.route('/api/health')
def health():
    """Info disclosure"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'internal_ip': '192.168.1.100',
        'vuln': 'Information Disclosure'
    })

@app.route('/api/metrics')
def metrics():
    """Exposed secrets"""
    return """
    app_database_password="super_secret_pass"
    app_api_key="sk_live_51234567890"
    """, 200, {'Content-Type': 'text/plain'}

@app.route('/swagger')
def swagger():
    """API disclosure"""
    return jsonify({
        'openapi': '3.0.0',
        'paths': {'/api/v1/users': {'vuln': 'Full API Disclosure'}}
    })

# SSRF
@app.route('/fetch_url', methods=['POST'])
def fetch_url():
    """SSRF vulnerability"""
    url = request.json.get('url')
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response:
            return jsonify({'content': response.read().decode()[:500], 'vuln': 'SSRF'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# XXE
@app.route('/parse_xml', methods=['POST'])
def parse_xml():
    """XXE vulnerability"""
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(request.data.decode())
        return jsonify({'parsed': ET.tostring(root).decode(), 'vuln': 'XXE'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CSRF
@app.route('/transfer_money', methods=['POST'])
def transfer_money():
    """CSRF - no token validation"""
    data = request.form or request.json
    return jsonify({
        'status': 'Transfer completed',
        'to': data.get('to_user'),
        'amount': data.get('amount'),
        'vuln': 'CSRF'
    })

# Open Redirect
@app.route('/redirect')
def open_redirect():
    """Open redirect"""
    return redirect(request.args.get('url', '/'))

# LDAP Injection
@app.route('/ldap_search')
def ldap_search():
    """LDAP injection"""
    username = request.args.get('username', '')
    return jsonify({
        'query': f"(&(objectClass=user)(uid={username}))",
        'vuln': 'LDAP Injection'
    })

# NoSQL Injection
@app.route('/nosql_login', methods=['POST'])
def nosql_login():
    """NoSQL injection"""
    data = request.json
    if isinstance(data.get('username'), dict) or isinstance(data.get('password'), dict):
        return jsonify({'status': 'Login successful', 'vuln': 'NoSQL Injection'})
    return jsonify({'error': 'Invalid credentials'}), 401

# Deserialization
@app.route('/deserialize', methods=['POST'])
def deserialize():
    """Insecure deserialization"""
    import pickle, base64
    try:
        obj = pickle.loads(base64.b64decode(request.json.get('data')))
        return jsonify({'result': str(obj), 'vuln': 'Insecure Deserialization'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Business Logic
@app.route('/purchase', methods=['POST'])
def purchase():
    """Negative quantity allowed"""
    data = request.json
    quantity = int(data.get('quantity', 1))
    total = 99.99 * quantity  # Can be negative!
    return jsonify({'total': total, 'vuln': 'Business Logic Flaw'})

# Race Condition
@app.route('/race_condition', methods=['POST'])
def race_condition():
    """Race condition"""
    import time
    time.sleep(0.1)  # Race window
    return jsonify({'status': 'Success', 'vuln': 'Race Condition'})

# Additional Vulnerabilities
@app.route('/weak_crypto')
def weak_crypto():
    """MD5 hashing"""
    data = request.args.get('data', 'test')
    return jsonify({'hash': hashlib.md5(data.encode()).hexdigest(), 'vuln': 'Weak Crypto'})

@app.route('/server_info')
def server_info():
    """Information disclosure"""
    import platform, sys
    return jsonify({
        'python': sys.version,
        'platform': platform.platform(),
        'vuln': 'Info Disclosure'
    })

@app.route('/.git/config')
def git_config():
    """Exposed .git"""
    return "[remote]\n  url = https://github.com/secret/repo.git", 200, {'Content-Type': 'text/plain'}

@app.route('/cookie_test')
def cookie_test():
    """Cookie vulnerability testing endpoint"""
    # Reflect cookie values (Cookie Injection)
    user_cookie = request.cookies.get('user', 'guest')
    role_cookie = request.cookies.get('role', 'user')
    admin_cookie = request.cookies.get('admin', 'false')
    
    return jsonify({
        'user': user_cookie,
        'role': role_cookie,
        'admin': admin_cookie,
        'vuln': 'Cookie Injection' if 'admin=true' in str(request.cookies) else None
    })

@app.route('/admin')
def admin_panel():
    """Admin panel with cookie-based auth (Cookie Poisoning)"""
    # VULN: No proper session validation
    session_cookie = request.cookies.get('PHPSESSID', '')
    user_role = request.cookies.get('user_role', 'guest')
    access_level = request.cookies.get('access_level', '0')
    
    # Vulnerable: Trusts cookie values
    if 'admin' in session_cookie.lower() or user_role == 'admin' or int(access_level) > 100:
        return jsonify({
            'message': 'Welcome to admin panel!',
            'secret': 'FLAG{COOKIE_POISONING_SUCCESS}',
            'vuln': 'Cookie Poisoning'
        })
    
    return jsonify({'error': 'Access denied'}), 403

if __name__ == '__main__':
    print("=" * 70)
    print("🎯 UNIFIED TRAINING ENVIRONMENT - OWASP Top 10 2025")
    print("=" * 70)
    print("⚠️  DELIBERATELY VULNERABLE - For AI Training Only!")
    print("=" * 70)
    print("\n📋 Features:")
    print("   • Original blog vulnerabilities")
    print("   • 50+ OWASP 2025 endpoints")
    print("   • 25+ vulnerability types")
    print("   • REST API, GraphQL, OAuth")
    print("   • File inclusion, SSRF, XXE")
    print("   • All modern attack vectors")
    init_db()
    print("\n🚀 Starting on http://localhost:5001\n")
    print("=" * 70)
    app.run(port=5001, debug=True)
