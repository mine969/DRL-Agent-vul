from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, make_response
import sqlite3
import jwt
import datetime
import hashlib
import os
import random
import string
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secure_blog_secret_key_2025'
JWT_SECRET = 'jwt_secret_key_secure_2025'
DB_NAME = 'blog.db'

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  role TEXT)''')
    
    # Posts Table
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, 
                  content TEXT, 
                  author_id INTEGER,
                  FOREIGN KEY(author_id) REFERENCES users(id))''')
                  
    # Comments Table
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  post_id INTEGER, 
                  content TEXT, 
                  author_name TEXT,
                  FOREIGN KEY(post_id) REFERENCES posts(id))''')
    
    # Seed Data
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        print("🌱 Seeding database...")
        # Users
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  ('admin', 'secure_password_123', 'admin'))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  ('guest', 'guest', 'user'))
        
        # Posts
        c.execute("INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                  ('Welcome to Secure Blog', 'This is our new full-stack blog with JWT auth!', 1))
        c.execute("INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                  ('JWT Security', 'JSON Web Tokens are stateless and secure if used correctly.', 1))
        c.execute("INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                  ('Database Security', 'Always sanitize your inputs to prevent SQL Injection.', 1))
        
        # Comments
        c.execute("INSERT INTO comments (post_id, content, author_name) VALUES (?, ?, ?)",
                  (1, 'Great post!', 'Guest User'))
                  
        conn.commit()
        
    conn.close()

# Initialize DB on start
init_db()

# --- HELPERS ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        # Check cookie (hybrid support)
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

if __name__ == '__main__':
    app.run(port=5000)
