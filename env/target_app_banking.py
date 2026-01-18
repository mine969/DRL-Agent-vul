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
        {{ content | safe }}
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
            ('john_smith', hashlib.md5(b'password').hexdigest(), 5420.50, '1002'),
            ('sarah_johnson', hashlib.md5(b'password').hexdigest(), 12350.75, '1003'),
            ('mike_williams', hashlib.md5(b'password').hexdigest(), 3200.00, '1004'),
            ('emily_brown', hashlib.md5(b'password').hexdigest(), 8750.25, '1005'),
            ('david_jones', hashlib.md5(b'password').hexdigest(), 25000.00, '1006'),
            ('lisa_garcia', hashlib.md5(b'password').hexdigest(), 1850.50, '1007'),
            ('tech_corp', hashlib.md5(b'password').hexdigest(), 150000.00, '2001'),
            ('retail_store', hashlib.md5(b'password').hexdigest(), 45000.00, '2002'),
            ('freelancer_alex', hashlib.md5(b'password').hexdigest(), 6200.00, '1008')
        ]
        c.executemany('INSERT INTO users (username, password, balance, account_number) VALUES (?, ?, ?, ?)', users)
        
        # Create realistic transaction history
        transactions = [
            # john_smith transactions
            (2, 2500.00, 'Salary Deposit - TechCorp Inc'),
            (2, -1200.00, 'Rent Payment - Landlord'),
            (2, -85.50, 'Grocery Store - Whole Foods'),
            (2, -45.00, 'Gas Station - Shell'),
            (2, -120.00, 'Electric Bill - City Power'),
            (2, -500.00, 'Transfer to Savings'),
            
            # sarah_johnson transactions
            (3, 4500.00, 'Salary Deposit - Design Studio'),
            (3, -1500.00, 'Mortgage Payment'),
            (3, -250.00, 'Car Payment - Auto Finance'),
            (3, -95.75, 'Restaurant - Italian Bistro'),
            (3, -180.00, 'Internet & Cable'),
            (3, -420.00, 'Insurance Premium'),
            
            # mike_williams transactions
            (4, 3000.00, 'Salary Deposit'),
            (4, -950.00, 'Rent Payment'),
            (4, -150.00, 'Phone Bill'),
            (4, -75.00, 'Gym Membership'),
            (4, -200.00, 'Student Loan Payment'),
            
            # emily_brown transactions
            (5, 3800.00, 'Salary Deposit - Marketing Co'),
            (5, -1100.00, 'Rent Payment'),
            (5, -320.00, 'Shopping - Fashion Outlet'),
            (5, -65.00, 'Coffee Shop - Starbucks'),
            (5, -150.00, 'Utilities'),
            (5, -500.00, 'Investment Transfer'),
            
            # david_jones transactions
            (6, 8000.00, 'Salary Deposit - Senior Manager'),
            (6, -2200.00, 'Mortgage Payment'),
            (6, -450.00, 'Car Lease'),
            (6, -1200.00, 'Private School Tuition'),
            (6, -350.00, 'Home Insurance'),
            (6, -180.00, 'Landscaping Service'),
            
            # lisa_garcia transactions
            (7, 2200.00, 'Salary Deposit - Retail'),
            (7, -800.00, 'Rent Payment'),
            (7, -120.00, 'Grocery Shopping'),
            (7, -55.00, 'Gas'),
            (7, -90.00, 'Phone Bill'),
            
            # tech_corp transactions
            (8, 50000.00, 'Client Payment - Project Alpha'),
            (8, -15000.00, 'Payroll - Monthly'),
            (8, -3500.00, 'Office Rent'),
            (8, -2200.00, 'Software Licenses'),
            (8, -1800.00, 'Marketing Campaign'),
            (8, 25000.00, 'Investment Round'),
            
            # retail_store transactions
            (9, 12000.00, 'Sales Revenue - Week 1'),
            (9, -4500.00, 'Inventory Purchase'),
            (9, -2000.00, 'Employee Wages'),
            (9, -850.00, 'Store Rent'),
            (9, -320.00, 'Utilities'),
            (9, 8500.00, 'Sales Revenue - Week 2'),
            
            # freelancer_alex transactions
            (10, 1500.00, 'Client Payment - Web Design'),
            (10, 2200.00, 'Client Payment - Logo Design'),
            (10, -650.00, 'Rent Payment'),
            (10, -120.00, 'Software Subscription'),
            (10, -85.00, 'Coworking Space'),
            (10, 1800.00, 'Client Payment - Branding')
        ]
        c.executemany('INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)', transactions)
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
    
    page_content = """
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
    """
    return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', page_content))

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
    
    page_content = """
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
                    <small style="color: var(--text-muted); font-size: 0.85rem;">Enter recipient account number</small>
                </div>
                <div class="form-group">
                    <label>Amount (USD)</label>
                    <input type="number" name="amount" class="form-control" placeholder="0.00" step="0.01" min="0.01" required>
                </div>
                <button type="submit" class="btn">Send Money</button>
            </form>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                <a href="/transfer-form" style="color: var(--primary); text-decoration: none; font-size: 0.9rem;">Advanced Transfer →</a>
            </div>
        </div>
        
        <div class="card">
            <h3 style="margin-bottom: 1rem;">Recent Transactions</h3>
            {% if transactions %}
            <ul class="transaction-list">
                {% for t in transactions[:10] %}
                <li class="transaction-item">
                    <div>
                        <div class="t-desc">{{ t.description }}</div>
                        <div class="t-date">{{ t.date }}</div>
                    </div>
                    <div class="t-amount {% if t.amount < 0 %}negative{% else %}positive{% endif %}">
                        {{ "$" if t.amount > 0 else "-$" }}{{ "%.2f"|format(t.amount|abs) }}
                    </div>
                </li>
                {% endfor %}
            </ul>
            {% if transactions|length > 10 %}
            <div style="text-align: center; padding-top: 1rem; border-top: 1px solid var(--border);">
                <p style="color: var(--text-muted); font-size: 0.9rem;">Showing 10 most recent transactions</p>
            </div>
            {% endif %}
            {% else %}
            <div style="text-align: center; color: var(--text-muted); padding: 2rem;">
                <p>No transaction history yet.</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">Your transactions will appear here.</p>
            </div>
            {% endif %}
        </div>
    </div>
    """
    
    return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', page_content), user=user, transactions=transactions)

@app.route('/transfer', methods=['POST'])
def transfer():
    # VULN: CSRF (No token)
    if 'user_id' not in session:
        return redirect('/')
    
    to_account = request.form.get('to_account', '').strip()
    try:
        amount = float(request.form.get('amount', 0))
    except (ValueError, TypeError):
        return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', 
            '<div class="alert alert-danger">Invalid amount. Please try again.</div>'))
    
    if amount <= 0:
        return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', 
            '<div class="alert alert-danger">Amount must be greater than zero.</div>'))
    
    conn = get_db()
    sender = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    recipient = conn.execute('SELECT * FROM users WHERE account_number = ?', (to_account,)).fetchone()
    
    msg = ""
    status = "error"
    
    if not to_account:
        msg = "Transfer failed: Please provide a recipient account number"
    elif sender['balance'] < amount:
        msg = f"Transfer failed: Insufficient funds. You have ${sender['balance']:.2f} but tried to transfer ${amount:.2f}"
    elif not recipient:
        msg = f"Transfer failed: Account number {to_account} not found"
    elif recipient['id'] == sender['id']:
        msg = "Transfer failed: Cannot transfer to your own account"
    else:
        # VULN: Can transfer to any account (IDOR)
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, sender['id']))
        conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient['id']))
        conn.execute('INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)', 
                    (sender['id'], -amount, f"Transfer to {to_account} - {recipient['username']}"))
        conn.execute('INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)', 
                    (recipient['id'], amount, f"Transfer from {sender['account_number']} - {sender['username']}"))
        conn.commit()
        msg = f"Transfer successful! ${amount:.2f} sent to account {to_account}"
        status = "success"
    
    conn.close()
    
    # Return HTML status page
    page_content = f"""
    <div style="text-align: center; margin-top: 4rem;">
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <h2 style="color: var(--primary);">Transaction Status</h2>
            <div class="alert {'alert-success' if status == 'success' else 'alert-danger'}" style="margin: 2rem 0;">
                {msg}
            </div>
            <div style="display: flex; gap: 1rem; justify-content: center;">
                <a href="/dashboard" class="btn">Return to Dashboard</a>
                <a href="/transfer-form" class="btn" style="background: var(--card-bg); color: var(--text-main); border: 1px solid var(--border);">Make Another Transfer</a>
            </div>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', page_content))

@app.route('/transfer-form')
def transfer_form():
    """Standalone transfer form"""
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    page_content = """
    <div style="max-width: 600px; margin: 0 auto; margin-top: 2rem;">
        <h1 style="color: var(--primary); margin-bottom: 2rem;">Money Transfer</h1>
        
        <div class="card">
            <div style="background: rgba(37, 99, 235, 0.1); padding: 1rem; border-radius: 6px; margin-bottom: 2rem;">
                <p style="margin: 0; color: var(--primary); font-weight: 600;">Available Balance: ${{ "%.2f"|format(user.balance) }}</p>
            </div>
            
            <form method="POST" action="/transfer">
                <div class="form-group">
                    <label>Recipient Account Number</label>
                    <input type="text" name="to_account" class="form-control" placeholder="e.g., 1002" required>
                    <small style="color: var(--text-muted); font-size: 0.85rem;">Enter the account number of the recipient</small>
                </div>
                <div class="form-group">
                    <label>Amount (USD)</label>
                    <input type="number" name="amount" class="form-control" placeholder="0.00" step="0.01" min="0.01" required>
                </div>
                <div class="form-group">
                    <label>Description (Optional)</label>
                    <input type="text" name="description" class="form-control" placeholder="e.g., Payment for services">
                </div>
                <button type="submit" class="btn">Send Money</button>
                <a href="/dashboard" style="margin-left: 1rem; color: var(--text-muted); text-decoration: none;">Cancel</a>
            </form>
        </div>
        
        <div class="card" style="margin-top: 2rem; background: rgba(255, 193, 7, 0.1); border-color: #FFC107;">
            <h3 style="margin-bottom: 1rem; color: #F57C00;">Recent Recipients</h3>
            <p style="color: var(--text-muted); font-size: 0.9rem;">
                Demo accounts: 1002 (john_smith), 1003 (sarah_johnson), 1004 (mike_williams)
            </p>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', page_content), user=dict(user))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("=" * 70)
    print("VULNERABLE BANKING APP - Research Variant 3")
    print("=" * 70)
    print("Starting on http://localhost:5004")
    init_db()
    app.run(port=5004, debug=True)
