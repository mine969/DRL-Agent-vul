"""
 VULNERABLE SOCIAL MEDIA PLATFORM - Research Variant 2
=========================================================

A deliberately vulnerable social media application for AI security training.
Focus: XSS, authentication, file uploads, IDOR

 DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, jsonify, session, send_from_directory, render_template_string, redirect, url_for
import sqlite3
import hashlib
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'social_secret_2025'
DB_NAME = 'env/social.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# MODERN UI TEMPLATES
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialNet | Connect the World</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2D88FF;
            --bg: #18191A;
            --card-bg: #242526;
            --text-main: #E4E6EB;
            --text-muted: #B0B3B8;
            --border: #3E4042;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
        }
        .navbar {
            background: var(--card-bg);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
        }
        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            margin-left: 2rem;
            font-weight: 500;
        }
        .nav-links a:hover { color: var(--text-main); }
        .container {
            max-width: 900px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        /* Cards & Feed */
        .card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .post-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #3a3b3c;
            margin-right: 1rem;
        }
        .post-content { font-size: 1.1rem; margin-bottom: 1rem; }
        .post-actions {
            border-top: 1px solid var(--border);
            padding-top: 0.5rem;
            display: flex;
            gap: 1rem;
        }
        
        /* Forms */
        .form-control {
            width: 100%;
            padding: 12px;
            background: #3A3B3C;
            border: none;
            border-radius: 6px;
            color: white;
            margin-bottom: 1rem;
            box-sizing: border-box;
        }
        .btn {
            background: var(--primary);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        .btn-outline {
            background: transparent;
            border: 1px solid var(--primary);
            color: var(--primary);
        }
        
        .alert {
            padding: 1rem;
            background: rgba(255, 76, 76, 0.2);
            color: #ff4c4c;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">SocialNet</a>
        <div class="nav-links">
            <a href="/">Feed</a>
            {% if session.user_id %}
                <a href="/profile/{{ session.user_id }}">My Profile</a>
                <a href="/messages/{{ session.user_id }}">Messages</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/register">Join</a>
            {% endif %}
        </div>
    </nav>
    
    <div class="container">
        {% if error %}<div class="alert">{{ error }}</div>{% endif %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration - VULN: Weak password validation"""
    if request.method == 'GET':
        form_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <h2 style="text-align: center; color: var(--primary);">Join SocialNet</h2>
            <form method="POST" action="/register">
                <input type="text" name="username" class="form-control" placeholder="Username" required>
                <input type="email" name="email" class="form-control" placeholder="Email" required>
                <input type="password" name="password" class="form-control" placeholder="Password" required>
                <button type="submit" class="btn">Sign Up</button>
            </form>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        return render_template_string(form_html)

    # POST Logic
    data = request.form if request.form else request.json
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashlib.md5(password.encode()).hexdigest()))
        conn.commit()
        return redirect('/login?msg=Welcome! Please login.')
    except Exception as e:
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', f'<div class="alert">Error: {str(e)}</div>'))
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login - VULN: Session fixation"""
    if request.method == 'GET':
        msg = request.args.get('msg', '')
        form_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="card" style="max-width: 400px; margin: 0 auto; margin-top: 50px;">
            <h2 style="text-align: center; color: var(--primary);">Login</h2>
            {% if msg %}<div class="alert" style="background: rgba(45, 136, 255, 0.2); color: white;">{{ msg }}</div>{% endif %}
            <form method="POST" action="/login">
                <input type="text" name="username" class="form-control" placeholder="Username" required>
                <input type="password" name="password" class="form-control" placeholder="Password" required>
                <button type="submit" class="btn">Log In</button>
            </form>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE).replace('{{ msg }}', msg)
        return render_template_string(form_html, msg=msg)

    # POST Logic
    data = request.form if request.form else request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                       (username, hashlib.md5(password.encode()).hexdigest())).fetchone()
    conn.close()
    
    if user:
        # VULN: Session fixation
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/posts')
    
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '<div class="alert">Invalid Credentials</div>'))

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

@app.route('/profile/<user_id>', methods=['GET'])
def profile(user_id):
    """User profile - VULN: IDOR"""
    conn = get_db()
    
    # VULN: No privacy check - can view private profiles
    user = conn.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    conn.close()
    
    if user:
        profile_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="card" style="margin-top: 2rem;">
            <div style="background: linear-gradient(90deg, var(--primary), #888); height: 150px; border-radius: 8px 8px 0 0;"></div>
            <div style="padding: 2rem; position: relative;">
                <div style="width: 120px; height: 120px; border-radius: 50%; background: #333; border: 4px solid var(--card-bg); position: absolute; top: -60px;"></div>
                <div style="margin-top: 40px;">
                    <h1>{{ u.username }}</h1>
                    <p style="color: #ccc;">{{ u.bio }}</p>
                    <div style="margin-top: 1rem;">
                        <button class="btn" style="width: auto;">Follow</button>
                        <button class="btn btn-outline" style="width: auto;">Message</button>
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        return render_template_string(profile_html, u=user)
    
    return "User not found", 404

# ============================================================================
# POSTS
# ============================================================================

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    """Posts - VULN: Stored XSS"""
    conn = get_db()
    
    if request.method == 'GET':
        posts = conn.execute('SELECT p.*, u.username, u.avatar FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC').fetchall()
        conn.close()
        
        feed_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="row">
            <div class="col" style="max-width: 600px; margin: 0 auto;">
                {% if session.user_id %}
                <div class="card">
                    <form action="/posts" method="POST">
                        <textarea name="content" class="form-control" placeholder="What's on your mind?" rows="3"></textarea>
                        <div style="text-align: right;">
                            <button type="submit" class="btn" style="width: auto;">Post</button>
                        </div>
                    </form>
                </div>
                {% endif %}
                
                {% for p in posts %}
                <div class="card">
                    <div class="post-header">
                        <div class="avatar"></div> <!-- Placeholder for avatar img -->
                        <div>
                            <div style="font-weight: bold;">{{ p.username }}</div>
                            <div style="font-size: 0.8rem; color: #B0B3B8;">{{ p.created_at }}</div>
                        </div>
                    </div>
                    <div class="post-content">
                        {{ p.content | safe }} <!-- VULN: XSS is rendered here -->
                    </div>
                    {% if p.image_url %}
                    <img src="/static/{{ p.image_url }}" style="width: 100%; border-radius: 8px; margin-top: 10px;">
                    {% endif %}
                    <div class="post-actions">
                        <button class="btn btn-outline" style="width: auto;">Like ({{ p.likes }})</button>
                        <a href="/posts/{{ p.id }}" class="btn btn-outline" style="width: auto; text-decoration: none;">Comment</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        return render_template_string(feed_html, posts=posts)
    
    elif request.method == 'POST':
        data = request.form if request.form else request.json
        user_id = session.get('user_id', 1)
        content = data.get('content', '')
        
        # VULN: Stored XSS - no sanitization
        conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
        conn.commit()
        conn.close()
        
        return redirect('/posts')

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

@app.route('/search', methods=['GET'])
def search():
    """Search - VULN: SQL Injection"""
    query = request.args.get('q', '')
    
    conn = get_db()
    # VULN: SQL Injection
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR bio LIKE '%{query}%'"
    
    try:
        results = conn.execute(sql).fetchall()
        conn.close()
        
        search_html = """
        {% extends "layout" %}
        {% block content %}
        <div style="margin-bottom: 2rem;">
            <h1>Search Results for "{{ q }}"</h1>
        </div>
        
        {% for u in results %}
        <div class="card">
            <div style="display: flex; align-items: center;">
                <div class="avatar" style="width: 60px; height: 60px;"></div>
                <div>
                    <h2><a href="/profile/{{ u.id }}" style="color: white; text-decoration: none;">{{ u.username }}</a></h2>
                    <p>{{ u.bio }}</p>
                </div>
            </div>
        </div>
        {% endfor %}
        
        {% if not results %}
        <p>No users found.</p>
        {% endif %}
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        return render_template_string(search_html, results=results, q=query)

    except Exception as e:
        conn.close()
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', f'<div class="alert">Database Error: {str(e)}</div>'))

# ============================================================================
# MISC
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'app': 'Social Media Platform'})

@app.route('/')
def index():
    return redirect('/posts')

if __name__ == '__main__':
    print("=" * 70)
    print("VULNERABLE SOCIAL MEDIA - Research Variant 2")
    print("=" * 70)
    print("DELIBERATELY VULNERABLE - For Research & Training Only!")
    print("=" * 70)
    print("\nFocus Areas:")
    print("   • XSS (stored in posts/comments, reflected in search)")
    print("   • Authentication (weak passwords, session fixation, predictable tokens)")
    print("   • File uploads (unrestricted, path traversal)")
    print("   • IDOR (profiles, messages, posts)")
    print("   • CSRF (friend requests)")
    print("   • SQL injection in search")
    init_db()
    print("\n Starting on http://localhost:5003\n")
    print("=" * 70)
    app.run(port=5003, debug=True)
