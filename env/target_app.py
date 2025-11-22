from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Vulnerable Login Page (SQL Injection)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # VULNERABILITY: SQL Injection
        # In a real app, this would be a DB query. Here we simulate it.
        # If the user inputs "' OR '1'='1", it bypasses the check.
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        if "' OR '1'='1" in query or (username == 'admin' and password == 'secret'):
            return "Welcome Admin! Flag: SQLI_SUCCESS"
        else:
            return "Invalid credentials"
            
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="text" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# Vulnerable Search Page (Reflected XSS)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULNERABILITY: Reflected XSS
    return f"<h1>Search Results for: {query}</h1>"

# VULNERABILITY: Security Misconfiguration (A05)
# Exposed debug endpoint with sensitive info
@app.route('/admin/debug')
def admin_debug():
    return "DEBUG INFO: SECRET_KEY = 'super_secret_key_123'; DB_HOST = 'localhost'"

# VULNERABILITY: Command Injection (A03)
# Simulating a ping utility
@app.route('/ping')
def ping():
    ip = request.args.get('ip', '')
    # VULNERABILITY: Command Injection
    # If ip is "127.0.0.1; cat /etc/passwd", we simulate the output
    if ';' in ip:
        cmd = ip.split(';')[1].strip()
        if 'cat /etc/passwd' in cmd:
            return "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin"
    return f"Pinging {ip}... Reply from {ip}: bytes=32 time=10ms TTL=64"

# VULNERABILITY: Broken Access Control / IDOR (A01)
@app.route('/profile')
def profile():
    user_id = request.args.get('user_id', '1')
    # VULNERABILITY: IDOR
    # ID 1 is guest, ID 2 is admin
    if user_id == '2':
        return "User Profile: Admin (ID: 2) | Email: admin@example.com | Role: SuperUser"
    return "User Profile: Guest (ID: 1) | Email: guest@example.com | Role: User"

# VULNERABILITY: SSRF (A10)
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url', '')
    # VULNERABILITY: SSRF
    # Allows fetching internal endpoints
    if 'localhost' in url or '127.0.0.1' in url:
        if '/admin/debug' in url:
            return "DEBUG INFO: SECRET_KEY = 'super_secret_key_123'; DB_HOST = 'localhost'"
        return f"Fetched internal content from {url}"
    return f"Fetched content from {url}"

@app.route('/')
def index():
    return '''
        <h1>Vulnerable App (OWASP Top 10)</h1>
        <a href="/login">Login (SQLi)</a><br>
        <a href="/search">Search (XSS)</a><br>
        <a href="/ping">Ping (Cmd Inj)</a><br>
        <a href="/profile?user_id=1">Profile (IDOR)</a><br>
        <a href="/fetch">Fetch (SSRF)</a>
    '''

if __name__ == '__main__':
    app.run(port=5000)
