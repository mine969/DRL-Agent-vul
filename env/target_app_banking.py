"""
 VULNERABLE BANKING APPLICATION - Research Variant 3
=====================================================

A deliberately vulnerable banking application for AI security training.
Focus: CSRF, IDOR, Logic Flaws, XSS

 DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, session, redirect, url_for, render_template_string, make_response
import sqlite3
import hashlib
import random

app = Flask(__name__)
app.secret_key = 'banking_secret_2025'
DB_NAME = 'env/banking.db'

# ============================================================================
# MODERN UI TEMPLATES
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureBank | Next-Gen Finance</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563EB;
            --primary-dark: #1E40AF;
            --secondary: #10B981;
            --bg: #F3F4F6;
            --card-bg: white;
            --text-main: #1F2937;
            --text-muted: #6B7280;
            --border: #E5E7EB;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            line-height: 1.5;
        }
        .navbar {
            background: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
            letter-spacing: -0.02em;
        }
        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            margin-left: 1.5rem;
            font-weight: 500;
            font-size: 0.95rem;
        }
        .nav-links a:hover { color: var(--text-main); }
        .container {
            max-width: 1000px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 2rem;
            border: 1px solid var(--border);
        }
        
        h1, h2, h3 { margin-top: 0; color: #111827; }
        
        .balance-hero {
            text-align: center;
            padding: 2rem 0;
        }
        .balance-amount {
            font-size: 4rem;
            font-weight: 800;
            color: #111827;
            letter-spacing: -0.03em;
        }
        .balance-label {
            color: var(--text-muted);
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Modern Form */
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.9rem; }
        .form-control {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 1rem;
            transition: border-color 0.2s;
            box-sizing: border-box;
        }
        .form-control:focus { outline: none; border-color: var(--primary); ring: 2px solid var(--primary-light); }
        
        .btn {
            display: inline-flex;
            justify-content: center;
            align-items: center;
            background: var(--primary);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: background 0.2s;
            width: 100%;
            font-size: 1rem;
        }
        .btn:hover { background: var(--primary-dark); }
        
        .transaction-list { list-style: none; padding: 0; }
        .transaction-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid var(--border);
        }
        .transaction-item:last-child { border-bottom: none; }
        .t-desc { font-weight: 500; }
        .t-date { font-size: 0.85rem; color: var(--text-muted); }
        .t-amount { font-weight: 600; font-family: monospace; font-size: 1.1rem; }
        .positive { color: var(--secondary); }
        .negative { color: #EF4444; }
        
        .alert {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }
        .alert-success { background: #D1FAE5; color: #065F46; }
        .alert-danger { background: #FEE2E2; color: #991B1B; } 
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">SecureBank</a>
        <div class="nav-links">
            {% if session.user_id %}
                <span style="color: var(--text-main); font-weight: 600; margin-right: 1rem;">{{ session.username }}</span>
                <a href="/logout">Sign Out</a>
            {% else %}
                <a href="/">Login</a>
            {% endif %}
        </div>
    </nav>
    
    <div class="container">
        {% block content %}{% endblock %}
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
    
    login_html = """
    {% extends "layout" %}
    {% block content %}
    <div style="display: flex; justify-content: center; margin-top: 4rem;">
        <div class="card" style="width: 100%; max-width: 400px; text-align: center;">
            <h1 style="color: var(--primary);">Welcome Back</h1>
            <p style="color: var(--text-muted); margin-bottom: 2rem;">Secure Access Portal</p>
            
            <form method="POST" action="/login">
                <div class="form-group">
                    <input type="text" name="username" class="form-control" placeholder="Username" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" class="form-control" placeholder="Password" required>
                </div>
                <button type="submit" class="btn">Sign In</button>
            </form>
            <p style="margin-top: 1rem; font-size: 0.8rem; color: var(--text-muted);">Demo: admin/admin123</p>
        </div>
    </div>
    {% endblock %}
    """.replace('{% extends "layout" %}', HTML_TEMPLATE)
    return render_template_string(login_html)

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
    transactions = conn.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC', (session['user_id'],)).fetchall()
    conn.close()
    
    dashboard_html = """
    {% extends "layout" %}
    {% block content %}
    <div class="balance-hero">
        <p class="balance-label">Total Balance</p>
        <div class="balance-amount">${{ "%.2f"|format(user.balance) }}</div>
        <p style="color: var(--text-muted);">Account Number: <span style="font-family: monospace;">{{ user.account_number }}</span></p>
    </div>
    
    <div class="grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
        <div class="card">
            <h3>Quick Transfer</h3>
            <form method="POST" action="/transfer">
                <div class="form-group">
                    <label>Recipient Account</label>
                    <input type="text" name="to_account" class="form-control" placeholder="e.g., 1002" required>
                </div>
                <div class="form-group">
                    <label>Amount (USD)</label>
                    <input type="number" name="amount" class="form-control" placeholder="0.00" step="0.01" required>
                </div>
                <button type="submit" class="btn">Send Money</button>
            </form>
        </div>
        
        <div class="card">
            <h3>Recent Transactions</h3>
            <ul class="transaction-list">
                {% for t in transactions %}
                <li class="transaction-item">
                    <div>
                        <div class="t-desc">{{ t.description }}</div>
                        <div class="t-date">{{ t.date }}</div>
                    </div>
                    <div class="t-amount {% if t.amount < 0 %}negative{% else %}positive{% endif %}">
                        {{ "$" if t.amount > 0 else "-$" }}{{ "%.2f"|format(t.amount|abs) }}
                    </div>
                </li>
                {% else %}
                <li style="text-align: center; color: var(--text-muted); padding: 1rem;">No history available</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    {% endblock %}
    """.replace('{% extends "layout" %}', HTML_TEMPLATE)
    
    return render_template_string(dashboard_html, user=user, transactions=transactions)

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
    
    msg = ""
    if sender['balance'] >= amount and recipient:
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, sender['id']))
        conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient['id']))
        conn.execute('INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)', 
                    (sender['id'], -amount, f"Transfer to {to_account}"))
        conn.commit()
        msg = "Transfer successful"
    else:
        msg = "Transfer failed: Insufficient funds or invalid account"
    
    conn.close()
    
    # Return HTML success page
    success_html = """
    {% extends "layout" %}
    {% block content %}
    <div style="text-align: center; margin-top: 4rem;">
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <h2 style="color: var(--primary);">Transaction Status</h2>
            <p style="font-size: 1.2rem; margin: 2rem 0;">{{ msg }}</p>
            <a href="/dashboard" class="btn">Return to Dashboard</a>
        </div>
    </div>
    {% endblock %}
    """.replace('{% extends "layout" %}', HTML_TEMPLATE)
    return render_template_string(success_html, msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("=" * 70)
    print("VULNERABLE BANKING APP - Research Variant 3")
    print("=" * 70)
    print("🚀 Starting on http://localhost:5004")
    init_db()
    app.run(port=5004, debug=True)
