"""
📁 VULNERABLE FILE SHARING PLATFORM - Research Variant 5
========================================================

A deliberately vulnerable file sharing application for AI security training.
Focus: File Upload, Path Traversal, IDOR, XXE

⚠️ DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, session, redirect, render_template_string, send_file
import sqlite3
import hashlib
import os
import uuid

app = Flask(__name__)
app.secret_key = 'fileshare_secret_2025'
DB_NAME = 'env/fileshare.db'
UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML TEMPLATES
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head><title>FileShare Pro</title></head>
<body style="font-family: Arial; max-width: 900px; margin: 50px auto;">
    <h1>📁 FileShare Pro</h1>
    {% if session.get('username') %}
        <p>Welcome, {{ session.get('username') }}! <a href="/logout">Logout</a></p>
        
        <h2>Upload File</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="text" name="description" placeholder="Description">
            <input type="submit" value="Upload">
        </form>
        
        <h2>My Files</h2>
        <table border="1" cellpadding="10">
            <tr><th>Filename</th><th>Description</th><th>Actions</th></tr>
            {% for file in files %}
            <tr>
                <td>{{ file.filename }}</td>
                <td>{{ file.description }}</td>
                <td>
                    <a href="/download/{{ file.id }}">Download</a> | 
                    <a href="/delete/{{ file.id }}">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </table>
    {% else %}
        <p><a href="/login">Login</a> | <a href="/register">Register</a></p>
    {% endif %}
</body>
</html>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Login - FileShare</title></head>
<body style="font-family: Arial; max-width: 400px; margin: 100px auto;">
    <h2>Login to FileShare</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <input type="submit" value="Login">
    </form>
    <p><a href="/register">Register</a> | <a href="/">Home</a></p>
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
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        filepath TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', hashlib.md5(b'admin123').hexdigest()),
            ('user', hashlib.md5(b'password').hexdigest())
        ]
        c.executemany('INSERT INTO users (username, password) VALUES (?, ?)', users)
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        conn = get_db()
        files = conn.execute('SELECT * FROM files WHERE user_id = ?', (session['user_id'],)).fetchall()
        conn.close()
        return render_template_string(HOME_PAGE, files=files, session=session)
    
    return render_template_string(HOME_PAGE, files=[], session=session)

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

@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')
    
    if 'file' not in request.files:
        return "No file", 400
    
    file = request.files['file']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return "No filename", 400
    
    # VULN: Unrestricted file upload - no validation
    filename = file.filename
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    
    conn = get_db()
    conn.execute('INSERT INTO files (user_id, filename, filepath, description) VALUES (?, ?, ?, ?)',
                (session['user_id'], filename, filepath, description))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/download/<int:file_id>')
def download(file_id):
    # VULN: IDOR - no authorization check
    conn = get_db()
    file_record = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    conn.close()
    
    if not file_record:
        return "File not found", 404
    
    # VULN: Path traversal possible
    return send_file(file_record['filepath'], as_attachment=True, download_name=file_record['filename'])

@app.route('/delete/<int:file_id>')
def delete(file_id):
    # VULN: IDOR - can delete anyone's files
    conn = get_db()
    file_record = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    
    if file_record:
        try:
            os.remove(file_record['filepath'])
        except:
            pass
        conn.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
    
    conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("=" * 70)
    print("📁 VULNERABLE FILE SHARING PLATFORM - Research Variant 5")
    print("=" * 70)
    print("🚀 Starting on http://localhost:5006")
    init_db()
    app.run(port=5006, debug=True)
