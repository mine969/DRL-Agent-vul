"""
📝 VULNERABLE BLOG PLATFORM - Research Variant 4
================================================

A deliberately vulnerable blog platform for AI security training.
Focus: XSS, SSTI, CSRF, File Inclusion

⚠️ DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, session, redirect, render_template_string
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'blog_secret_2025'
DB_NAME = 'env/blog.db'

# HTML TEMPLATES
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>VulnBlog - Share Your Stories</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #fafafa;
            color: #333;
        }
        .header {
            background: white;
            border-bottom: 1px solid #e6e6e6;
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #1a1a1a;
            text-decoration: none;
        }
        .nav a {
            margin-left: 20px;
            color: #666;
            text-decoration: none;
            font-size: 14px;
        }
        .nav a:hover { color: #1a1a1a; }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .post-card {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: box-shadow 0.3s;
        }
        .post-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }
        .post-card h3 {
            font-size: 24px;
            margin-bottom: 12px;
            color: #1a1a1a;
        }
        .post-card p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .post-meta {
            font-size: 13px;
            color: #999;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #1a1a1a;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
        }
        .btn:hover {
            background: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <a href="/" class="logo">📝 VulnBlog</a>
            <div class="nav">
                {% if session.get('username') %}
                    <span style="color: #666;">{{ session.get('username') }}</span>
                    <a href="/new-post" class="btn">Write</a>
                    <a href="/logout">Logout</a>
                {% else %}
                    <a href="/login">Sign In</a>
                    <a href="/register" class="btn">Get Started</a>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="container">
        <h2 style="margin-bottom: 30px; font-size: 32px;">Latest Stories</h2>
        {% for post in posts %}
            <div class="post-card">
                <h3>{{ post.title }}</h3>
                <p>{{ post.content | safe }}</p>
                <div class="post-meta">
                    By {{ post.author }} | <a href="/post/{{ post.id }}" style="color: #1a1a1a;">Read more →</a>
                </div>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sign In - VulnBlog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 16px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #1a1a1a;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        input[type="submit"] {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            cursor: pointer;
            margin-top: 10px;
        }
        .links {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
        }
        .links a {
            color: #1a1a1a;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>📝 Sign In to VulnBlog</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Sign In">
        </form>
        <div class="links">
            <a href="/register">Create account</a> | <a href="/">Home</a>
        </div>
    </div>
</body>
</html>
"""

POST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ post.title }} - VulnBlog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            color: #333;
        }
        .header {
            background: white;
            border-bottom: 1px solid #e6e6e6;
            padding: 15px 0;
        }
        .header-content {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #1a1a1a;
            text-decoration: none;
        }
        .container {
            max-width: 700px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .article {
            background: white;
            padding: 40px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .article h1 {
            font-size: 36px;
            margin-bottom: 20px;
            line-height: 1.3;
        }
        .article-meta {
            color: #999;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .article-content {
            font-size: 18px;
            line-height: 1.8;
            color: #333;
        }
        .comments {
            background: white;
            padding: 30px;
            border-radius: 8px;
        }
        .comment {
            border-left: 3px solid #1a1a1a;
            padding-left: 15px;
            margin: 20px 0;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: inherit;
            font-size: 14px;
            margin: 10px 0;
        }
        input[type="submit"] {
            padding: 10px 20px;
            background: #1a1a1a;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <a href="/" class="logo">📝 VulnBlog</a>
        </div>
    </div>
    
    <div class="container">
        <div class="article">
            <h1>{{ post.title }}</h1>
            <div class="article-meta">By {{ post.author }}</div>
            <div class="article-content">{{ post.content | safe }}</div>
        </div>
        
        <div class="comments">
            <h3 style="margin-bottom: 20px;">Comments ({{ comments|length }})</h3>
            {% for comment in comments %}
                <div class="comment">
                    <p>{{ comment.content | safe }}</p>
                    <small style="color: #999;">— {{ comment.author }}</small>
                </div>
            {% endfor %}
            
            <h4 style="margin-top: 30px; margin-bottom: 10px;">Add a comment</h4>
            <form method="POST" action="/post/{{ post.id }}/comment">
                <textarea name="content" rows="3" placeholder="Share your thoughts..." required></textarea>
                <input type="submit" value="Post Comment">
            </form>
        </div>
    </div>
</body>
</html>
"""

NEW_POST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Write a Story - VulnBlog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
        }
        .header {
            background: white;
            border-bottom: 1px solid #e6e6e6;
            padding: 15px 0;
        }
        .header-content {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .container {
            max-width: 700px;
            margin: 40px auto;
            padding: 0 20px;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: none;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: none;
            font-size: 18px;
            line-height: 1.8;
            min-height: 400px;
            font-family: inherit;
        }
        input[type="submit"] {
            padding: 12px 30px;
            background: #1a1a1a;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .editor {
            background: white;
            border-radius: 8px;
            padding: 30px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <a href="/" style="color: #1a1a1a; text-decoration: none; font-weight: bold;">📝 VulnBlog</a>
        </div>
    </div>
    
    <div class="container">
        <div class="editor">
            <form method="POST">
                <input type="text" name="title" placeholder="Title" required>
                <textarea name="content" placeholder="Tell your story..." required></textarea>
                <input type="submit" value="Publish">
                <a href="/" style="margin-left: 15px; color: #666; text-decoration: none;">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>
"""

# DATABASE
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', hashlib.md5(b'admin123').hexdigest()),
            ('blogger', hashlib.md5(b'password').hexdigest())
        ]
        c.executemany('INSERT INTO users (username, password) VALUES (?, ?)', users)
        
        c.execute('INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
                 (1, 'Welcome to VulnBlog!', 'This is a deliberately vulnerable blog platform for security research.'))
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    posts = conn.execute('''SELECT posts.*, users.username as author 
                           FROM posts JOIN users ON posts.user_id = users.id 
                           ORDER BY created_at DESC''').fetchall()
    conn.close()
    return render_template_string(HOME_PAGE, posts=posts, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                           (username, hashlib.md5(password.encode()).hexdigest())).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        return "Invalid credentials", 401
    
    return render_template_string(LOGIN_PAGE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, hashlib.md5(password.encode()).hexdigest()))
            conn.commit()
            return redirect('/login')
        except:
            return "Username already exists", 400
        finally:
            conn.close()
    
    return render_template_string(LOGIN_PAGE.replace('Login', 'Register'))

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        # VULN: Stored XSS - no sanitization
        conn = get_db()
        conn.execute('INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
                    (session['user_id'], title, content))
        conn.commit()
        conn.close()
        return redirect('/')
    
    return render_template_string(NEW_POST_PAGE)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = get_db()
    post = conn.execute('''SELECT posts.*, users.username as author 
                          FROM posts JOIN users ON posts.user_id = users.id 
                          WHERE posts.id = ?''', (post_id,)).fetchone()
    comments = conn.execute('''SELECT comments.*, users.username as author 
                              FROM comments JOIN users ON comments.user_id = users.id 
                              WHERE post_id = ?''', (post_id,)).fetchall()
    conn.close()
    
    if not post:
        return "Post not found", 404
    
    return render_template_string(POST_PAGE, post=post, comments=comments)

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    content = request.form.get('content')
    
    # VULN: Stored XSS
    conn = get_db()
    conn.execute('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
                (post_id, session['user_id'], content))
    conn.commit()
    conn.close()
    
    return redirect(f'/post/{post_id}')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("=" * 70)
    print("📝 VULNERABLE BLOG PLATFORM - Research Variant 4")
    print("=" * 70)
    print("🚀 Starting on http://localhost:5005")
    init_db()
    app.run(port=5005, debug=True)
