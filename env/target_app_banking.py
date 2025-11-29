"""
🏦 VULNERABLE BANKING APPLICATION - Research Variant 3
=====================================================

A deliberately vulnerable banking application for AI security training.
Focus: CSRF, IDOR, Logic Flaws, XSS

⚠️ DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, session, redirect, url_for, render_template_string, make_response
import sqlite3
import hashlib
import random

app = Flask(__name__)
app.secret_key = 'banking_secret_2025'
DB_NAME = 'env/banking.db'

# HTML TEMPLATES
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureBank - Online Banking</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 5px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        input[type="submit"]:hover {
            opacity: 0.9;
        }
        .hint {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🏦 SecureBank</h1>
            <p>Trusted Online Banking Since 2010</p>
        </div>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Sign In">
        </form>
        <div class="hint">Demo: admin/admin123 or user/password</div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - SecureBank</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 24px; }
        .header a {
            color: white;
            text-decoration: none;
            padding: 8px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .balance-card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .balance-card h2 {
            color: #667eea;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .balance-amount {
            font-size: 48px;
            font-weight: bold;
            color: #2d3748;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .card h3 {
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 20px;
        }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        input[type="submit"] {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            cursor: pointer;
            margin-top: 10px;
        }
        .transaction-list {
            list-style: none;
        }
        .transaction-list li {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
        }
        .transaction-list li:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏦 SecureBank</h1>
        <div>
            <span style="margin-right: 20px;">Welcome, {{ user.username }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="balance-card">
            <h2>Available Balance</h2>
            <div class="balance-amount">${{ "%.2f"|format(user.balance) }}</div>
            <p style="color: #666; margin-top: 10px;">Account #{{ user.account_number }}</p>
        </div>
        
        <div class="card">
            <h3>💸 Transfer Money</h3>
            <form method="POST" action="/transfer">
                <input type="text" name="to_account" placeholder="Recipient Account Number" required>
                <input type="number" name="amount" placeholder="Amount" step="0.01" required>
                <input type="submit" value="Transfer Now">
            </form>
        </div>
        
        <div class="card">
            <h3>📊 Recent Transactions</h3>
            <ul class="transaction-list">
            {% if transactions %}
                {% for t in transactions %}
                    <li>
                        <span>{{ t.description }}</span>
                        <span style="font-weight: bold; color: {% if t.amount < 0 %}#e53e3e{% else %}#38a169{% endif %};">
                            ${{ "%.2f"|format(t.amount) }}
                        </span>
                    </li>
                {% endfor %}
            {% else %}
                <li style="text-align: center; color: #999;">No transactions yet</li>
            {% endif %}
            </ul>
        </div>
    </div>
</body>
</html>
"""

# DATABASE SETUP
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        balance REAL,
        account_number TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Seed
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', hashlib.md5(b'admin123').hexdigest(), 100000.0, '1001'),
            ('user', hashlib.md5(b'password').hexdigest(), 500.0, '1002'),
            ('victim', hashlib.md5(b'secret').hexdigest(), 5000.0, '1003')
        ]
        c.executemany('INSERT INTO users (username, password, balance, account_number) VALUES (?, ?, ?, ?)', users)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                       (username, hashlib.md5(password.encode()).hexdigest())).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/dashboard')
    return "Invalid credentials", 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    transactions = conn.execute('SELECT * FROM transactions WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_PAGE, user=user, transactions=transactions)

@app.route('/transfer', methods=['POST'])
def transfer():
    # VULN: CSRF (No token)
    if 'user_id' not in session:
        return redirect('/')
    
    to_account = request.form.get('to_account')
    amount = float(request.form.get('amount'))
    
    conn = get_db()
    sender = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    recipient = conn.execute('SELECT * FROM users WHERE account_number = ?', (to_account,)).fetchone()
    
    if sender['balance'] >= amount and recipient:
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, sender['id']))
        conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient['id']))
        conn.execute('INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)', 
                    (sender['id'], -amount, f"Transfer to {to_account}"))
        conn.commit()
        msg = "Transfer successful"
    else:
        msg = "Transfer failed"
    
    conn.close()
    return f"{msg} <a href='/dashboard'>Back</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("=" * 70)
    print("🏦 VULNERABLE BANKING APP - Research Variant 3")
    print("=" * 70)
    print("🚀 Starting on http://localhost:5004")
    init_db()
    app.run(port=5004, debug=True)
