"""
📱 VULNERABLE SOCIAL MEDIA PLATFORM - Research Variant 2
=========================================================

A deliberately vulnerable social media application for AI security training.
Focus: XSS, authentication, file uploads, IDOR

⚠️ DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, jsonify, session, send_from_directory
import sqlite3
import hashlib
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'social_secret_2025'
DB_NAME = 'social.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        bio TEXT,
        avatar TEXT,
        is_private INTEGER DEFAULT 0,
        reset_token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        image_url TEXT,
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        content TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS friendships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        friend_id INTEGER,
        status TEXT DEFAULT 'pending'
    )''')
    
    # Seed data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', 'admin@social.com', hashlib.md5(b'admin123').hexdigest(), 'Admin user', 'admin.jpg', 0),
            ('alice', 'alice@social.com', hashlib.md5(b'password').hexdigest(), 'Hello world!', 'alice.jpg', 0),
            ('bob', 'bob@social.com', hashlib.md5(b'password').hexdigest(), 'Developer', 'bob.jpg', 1)
        ]
        c.executemany('INSERT INTO users (username, email, password, bio, avatar, is_private) VALUES (?, ?, ?, ?, ?, ?)', users)
        
        posts = [
            (1, 'Welcome to our social platform!', None, 10),
            (2, 'Just joined! Excited to be here.', None, 5),
            (3, 'Check out my new project', 'project.jpg', 15)
        ]
        c.executemany('INSERT INTO posts (user_id, content, image_url, likes) VALUES (?, ?, ?, ?)', posts)
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """User registration - VULN: Weak password validation"""
    data = request.json
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    # VULN: No password strength validation
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashlib.md5(password.encode()).hexdigest()))
        conn.commit()
        return jsonify({'message': 'User registered', 'vuln': 'Weak Password Validation'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Login - VULN: Session fixation"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                       (username, hashlib.md5(password.encode()).hexdigest())).fetchone()
    conn.close()
    
    if user:
        # VULN: Session fixation - doesn't regenerate session ID
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful', 'user': dict(user), 'vuln': 'Session Fixation'})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/password-reset', methods=['POST'])
def password_reset():
    """Password reset - VULN: Predictable reset tokens"""
    data = request.json
    email = data.get('email', '')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        # VULN: Predictable token (just user ID)
        reset_token = str(user['id'])
        conn.execute('UPDATE users SET reset_token = ? WHERE id = ?', (reset_token, user['id']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Reset token sent', 'token': reset_token, 'vuln': 'Predictable Reset Token'})
    
    conn.close()
    return jsonify({'error': 'User not found'}), 404

# ============================================================================
# PROFILES
# ============================================================================

@app.route('/api/profile/<user_id>', methods=['GET', 'PUT'])
def profile(user_id):
    """User profile - VULN: IDOR"""
    conn = get_db()
    
    if request.method == 'GET':
        # VULN: No privacy check - can view private profiles
        user = conn.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
        conn.close()
        return jsonify(dict(user)) if user else ('', 404)
    
    elif request.method == 'PUT':
        # VULN: No authorization - can edit any profile
        data = request.json
        conn.execute('UPDATE users SET bio = ?, is_private = ? WHERE id = ?',
                    (data.get('bio'), data.get('is_private'), user_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Profile updated', 'vuln': 'IDOR'})

# ============================================================================
# POSTS
# ============================================================================

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    """Posts - VULN: Stored XSS"""
    conn = get_db()
    
    if request.method == 'GET':
        posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify({'posts': [dict(p) for p in posts]})
    
    elif request.method == 'POST':
        data = request.json
        user_id = session.get('user_id', 1)
        content = data.get('content', '')
        
        # VULN: Stored XSS - no sanitization
        conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
        conn.commit()
        post_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        
        return jsonify({'message': 'Post created', 'post_id': post_id, 'vuln': 'Stored XSS'}), 201

@app.route('/api/posts/<post_id>', methods=['GET', 'DELETE'])
def post_detail(post_id):
    """Post detail - VULN: IDOR in delete"""
    conn = get_db()
    
    if request.method == 'GET':
        post = conn.execute(f"SELECT * FROM posts WHERE id = {post_id}").fetchone()
        conn.close()
        return jsonify(dict(post)) if post else ('', 404)
    
    elif request.method == 'DELETE':
        # VULN: No authorization - can delete any post
        conn.execute(f"DELETE FROM posts WHERE id = {post_id}")
        conn.commit()
        conn.close()
        return jsonify({'message': 'Post deleted', 'vuln': 'IDOR'})

# ============================================================================
# COMMENTS
# ============================================================================

@app.route('/api/posts/<post_id>/comments', methods=['GET', 'POST'])
def comments(post_id):
    """Comments - VULN: Reflected XSS"""
    conn = get_db()
    
    if request.method == 'GET':
        # VULN: Reflected XSS in search
        search = request.args.get('search', '')
        comments = conn.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,)).fetchall()
        conn.close()
        
        return jsonify({
            'comments': [dict(c) for c in comments],
            'search': search,  # VULN: Reflected without sanitization
            'vuln': 'Reflected XSS' if search else None
        })
    
    elif request.method == 'POST':
        data = request.json
        user_id = session.get('user_id', 1)
        content = data.get('content', '')
        
        # VULN: Stored XSS
        conn.execute('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
                    (post_id, user_id, content))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Comment added', 'vuln': 'Stored XSS'}), 201

# ============================================================================
# FILE UPLOADS
# ============================================================================

def allowed_file(filename):
    # VULN: Weak validation
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload - VULN: Unrestricted file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No filename'}), 400
    
    # VULN: Can bypass with double extension (e.g., shell.php.jpg)
    # VULN: No file content validation
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({
        'message': 'File uploaded',
        'filename': filename,
        'url': f'/uploads/{filename}',
        'vuln': 'Unrestricted File Upload'
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files - VULN: Path traversal"""
    # VULN: No path validation - path traversal possible
    return send_from_directory(UPLOAD_FOLDER, filename)

# ============================================================================
# MESSAGES
# ============================================================================

@app.route('/api/messages/<user_id>', methods=['GET'])
def get_messages(user_id):
    """Get messages - VULN: IDOR"""
    conn = get_db()
    # VULN: Can read anyone's messages
    messages = conn.execute('SELECT * FROM messages WHERE to_user_id = ? OR from_user_id = ?',
                           (user_id, user_id)).fetchall()
    conn.close()
    return jsonify({'messages': [dict(m) for m in messages], 'vuln': 'IDOR'})

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send message - VULN: Stored XSS"""
    data = request.json
    from_user_id = session.get('user_id', 1)
    to_user_id = data.get('to_user_id')
    content = data.get('content', '')
    
    conn = get_db()
    # VULN: No XSS protection
    conn.execute('INSERT INTO messages (from_user_id, to_user_id, content) VALUES (?, ?, ?)',
                (from_user_id, to_user_id, content))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Message sent', 'vuln': 'Stored XSS'}), 201

# ============================================================================
# FRIENDSHIPS
# ============================================================================

@app.route('/api/friends/add', methods=['POST'])
def add_friend():
    """Add friend - VULN: CSRF"""
    data = request.json
    user_id = session.get('user_id', 1)
    friend_id = data.get('friend_id')
    
    # VULN: No CSRF protection
    conn = get_db()
    conn.execute('INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, ?)',
                (user_id, friend_id, 'accepted'))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Friend added', 'vuln': 'CSRF'})

# ============================================================================
# SEARCH
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search():
    """Search - VULN: SQL Injection"""
    query = request.args.get('q', '')
    
    conn = get_db()
    # VULN: SQL Injection
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR bio LIKE '%{query}%'"
    
    try:
        results = conn.execute(sql).fetchall()
        conn.close()
        return jsonify({'results': [dict(r) for r in results], 'vuln': 'SQL Injection'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e), 'vuln': 'SQL Injection'}), 500

# ============================================================================
# MISC
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'app': 'Social Media Platform'})

@app.route('/')
def index():
    return jsonify({
        'message': 'Social Media API',
        'endpoints': ['/api/register', '/api/login', '/api/profile/<id>', '/api/posts', '/api/upload', '/api/messages/<id>', '/api/search']
    })

if __name__ == '__main__':
    print("=" * 70)
    print("📱 VULNERABLE SOCIAL MEDIA PLATFORM - Research Variant 2")
    print("=" * 70)
    print("⚠️  DELIBERATELY VULNERABLE - For Research & Training Only!")
    print("=" * 70)
    print("\n📋 Focus Areas:")
    print("   • XSS (stored in posts/comments, reflected in search)")
    print("   • Authentication (weak passwords, session fixation, predictable tokens)")
    print("   • File uploads (unrestricted, path traversal)")
    print("   • IDOR (profiles, messages, posts)")
    print("   • CSRF (friend requests)")
    print("   • SQL injection in search")
    init_db()
    print("\n🚀 Starting on http://localhost:5003\n")
    print("=" * 70)
    app.run(port=5003, debug=True)
