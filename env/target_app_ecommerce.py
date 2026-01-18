"""
🛒 VULNERABLE E-COMMERCE PLATFORM - Research Variant 1
=======================================================

A deliberately vulnerable e-commerce application for AI security training.
Focus: Business logic flaws, payment vulnerabilities, API security

⚠️ DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for
import sqlite3
import hashlib
import datetime
import jwt

app = Flask(__name__)
app.secret_key = 'ecommerce_secret_2025'
JWT_SECRET = 'ecommerce_jwt_secret'
DB_NAME = 'env/ecommerce.db'

# ============================================================================
# MODERN UI TEMPLATES
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberShop 2077 | Vulnerable E-Commerce</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00f2ff;
            --secondary: #7000ff;
            --bg: #0a0a12;
            --card-bg: #161622;
            --text: #e0e0e0;
            --accent: #ff0055;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            line-height: 1.6;
        }
        .navbar {
            background: rgba(22, 22, 34, 0.9);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--secondary);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
        }
        .nav-links a {
            color: var(--text);
            text-decoration: none;
            margin-left: 1.5rem;
            font-weight: 500;
            transition: color 0.3s;
        }
        .nav-links a:hover { color: var(--primary); }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .hero {
            text-align: center;
            padding: 4rem 1rem;
            background: radial-gradient(circle at center, #1a1a2e 0%, var(--bg) 70%);
        }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { color: #888; font-size: 1.2rem; }
        .btn {
            display: inline-block;
            background: var(--primary);
            color: #000;
            padding: 0.8rem 1.5rem;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 15px var(--primary);
        }
        .btn-secondary { background: var(--card-bg); color: var(--text); border: 1px solid var(--secondary); }
        .btn-secondary:hover { box-shadow: 0 0 15px var(--secondary); }
        
        /* Grid System */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #2a2a35;
            transition: transform 0.3s;
        }
        .card:hover { transform: translateY(-5px); border-color: var(--primary); }
        .card-img { width: 100%; height: 200px; object-fit: cover; background: #2a2a35; }
        .card-body { padding: 1.5rem; }
        .price { font-size: 1.25rem; color: var(--primary); font-weight: 700; }
        
        /* Forms */
        .form-group { margin-bottom: 1rem; }
        .form-control {
            width: 100%;
            padding: 0.8rem;
            background: #0f0f18;
            border: 1px solid #2a2a35;
            color: white;
            border-radius: 4px;
        }
        .form-control:focus { outline: none; border-color: var(--primary); }
        
        /* Alerts */
        .alert {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 4px;
            background: rgba(255, 0, 85, 0.1);
            border: 1px solid var(--accent);
            color: var(--accent);
        }
        .badge {
            background: var(--secondary);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">CONSUME.OBEY</a>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Shop</a>
            {% if session.user %}
                <a href="/dashboard">Dashboard ({{ session.user.username }})</a>
                <a href="/cart">Cart <span class="badge">{{ session.cart|length }}</span></a>
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            {% endif %}
        </div>
    </nav>
    
    <div class="container">
        {% if error %}
        <div class="alert">{{ error }}</div>
        {% endif %}
        
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
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'customer',
        balance REAL DEFAULT 100.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        stock INTEGER,
        category TEXT,
        image_url TEXT
    )''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total REAL,
        status TEXT DEFAULT 'pending',
        coupon_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Order items table
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL
    )''')
    
    # Coupons table
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        discount REAL,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0
    )''')
    
    # Seed data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Create users
        users = [
            ('admin', 'admin@shop.com', hashlib.md5(b'admin123').hexdigest(), 'admin', 10000.0),
            ('customer', 'customer@shop.com', hashlib.md5(b'password').hexdigest(), 'customer', 100.0),
            ('vip', 'vip@shop.com', hashlib.md5(b'vip123').hexdigest(), 'vip', 500.0)
        ]
        c.executemany('INSERT INTO users (username, email, password, role, balance) VALUES (?, ?, ?, ?, ?)', users)
        
        # Create products
        products = [
            ('Laptop Pro', 'High-performance laptop', 999.99, 50, 'Electronics', 'laptop.jpg'),
            ('Smartphone X', 'Latest smartphone', 699.99, 100, 'Electronics', 'phone.jpg'),
            ('Headphones', 'Noise-cancelling headphones', 199.99, 200, 'Audio', 'headphones.jpg'),
            ('Smart Watch', 'Fitness tracking watch', 299.99, 150, 'Wearables', 'watch.jpg'),
            ('Tablet', '10-inch tablet', 449.99, 75, 'Electronics', 'tablet.jpg'),
            ('Premium Course', 'Online security course', 0.01, 1000, 'Digital', 'course.jpg')
        ]
        c.executemany('INSERT INTO products (name, description, price, stock, category, image_url) VALUES (?, ?, ?, ?, ?, ?)', products)
        
        # Create coupons
        coupons = [
            ('SAVE10', 10.0, 100),
            ('SAVE50', 50.0, 10),
            ('FREE100', 100.0, 1),
            ('VIP20', 20.0, 50)
        ]
        c.executemany('INSERT INTO coupons (code, discount, max_uses) VALUES (?, ?, ?)', coupons)
    
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
    """User registration - VULN: Mass assignment"""
    if request.method == 'GET':
        form_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="row" style="margin-top: 50px;">
            <div class="col-md-6 offset-md-3">
                <div class="card">
                    <div class="card-body">
                        <h2 class="text-center" style="color: var(--primary);">Join the Network</h2>
                        <form method="POST" action="/register">
                            <div class="form-group">
                                <label>Username</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input type="email" name="email" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Password</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Initial Balance</label>
                                <input type="number" name="balance" class="form-control" value="100">
                            </div>
                            <button type="submit" class="btn" style="width: 100%;">Create Identity</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        return render_template_string(form_html)

    # POST Logic
    data = request.form if request.form else request.json
    conn = get_db()
    
    try:
        conn.execute(
            'INSERT INTO users (username, email, password, role, balance) VALUES (?, ?, ?, ?, ?)',
            (data.get('username'), data.get('email'), 
             hashlib.md5(data.get('password', '').encode()).hexdigest(),
             data.get('role', 'customer'),
             data.get('balance', 100.0))
        )
        conn.commit()
        return redirect('/login?msg=Registered successfully')
    except Exception as e:
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', f'<div class="alert">Error: {str(e)}</div>'))
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login - VULN: SQL Injection"""
    if request.method == 'GET':
        msg = request.args.get('msg', '')
        form_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="row" style="margin-top: 50px;">
            <div class="col-md-6 offset-md-3">
                <div class="card">
                    <div class="card-body">
                        <h2 class="text-center" style="color: var(--primary);">System Access</h2>
                        {% if msg %}<div class="alert">{{ msg }}</div>{% endif %}
                        <form method="POST" action="/login">
                            <div class="form-group">
                                <label>Username</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Password</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn" style="width: 100%;">Authenticate</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE, 1).replace('{{ msg }}', msg) # Simple replace for msg
        return render_template_string(form_html, msg=msg)

    # POST Logic
    data = request.form if request.form else request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = get_db()
    # VULN: SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashlib.md5(password.encode()).hexdigest()}'"
    
    try:
        user = conn.execute(query).fetchone()
        if user:
            session['user'] = dict(user)
            # Token logic kept for legacy API support if needed, but session is main
            token = jwt.encode({
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            return redirect('/products')
        
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '<div class="alert">Invalid Credentials</div>'))
    except Exception as e:
        # SQL Error
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', f'<div class="alert">Database Error: {str(e)}</div>'))
    finally:
        conn.close()

# ============================================================================
# PRODUCTS
# ============================================================================

@app.route('/products', methods=['GET'])
def get_products():
    """Get products - VULN: SQL Injection in search"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    conn = get_db()
    
    if search:
        query = f"SELECT * FROM products WHERE name LIKE '%{search}%' OR description LIKE '%{search}%'"
    elif category:
        query = f"SELECT * FROM products WHERE category = '{category}'"
    else:
        query = "SELECT * FROM products"
    
    try:
        products = conn.execute(query).fetchall()
        
        # HTML Render
        products_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="hero" style="padding: 2rem;">
            <h1>Latest Tech Drops</h1>
            <p>Secure your hardware. Upgrade your reality.</p>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <form action="/products" method="GET" class="d-flex" style="max-width: 500px; margin: 0 auto;">
                    <input type="text" name="search" class="form-control" placeholder="Search exploits, hardware, tools...">
                    <button class="btn btn-secondary" type="submit" style="margin-left: 10px;">Scan</button>
                </form>
            </div>
        </div>

        <div class="grid">
            {% for p in products %}
            <div class="card">
                <div class="card-img" style="background-image: url('/static/{{ p.image_url }}'); display: flex; align-items: center; justify-content: center; color: #555;">
                    [IMG: {{ p.name }}]
                </div>
                <div class="card-body">
                    <h3>{{ p.name }}</h3>
                    <p class="price">${{ p.price }}</p>
                    <a href="/product/{{ p.id }}" class="btn">View Specs</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        
        return render_template_string(products_html, products=products)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', f'<div class="alert">Database Error: {str(e)}</div>'))
    finally:
        conn.close()

@app.route('/product/<product_id>', methods=['GET'])
def product_detail(product_id):
    """Product detail - VULN: IDOR"""
    conn = get_db()
    product = conn.execute(f"SELECT * FROM products WHERE id = {product_id}").fetchone()
    conn.close()
    
    if product:
        detail_html = """
        {% extends "layout" %}
        {% block content %}
        <div class="row" style="margin-top: 40px; display: flex; gap: 40px;">
            <div class="col" style="flex: 1;">
                <div style="height: 400px; background: #2a2a35; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                    <h1>[Product Image]</h1>
                </div>
            </div>
            <div class="col" style="flex: 1;">
                <h1 style="font-size: 3rem; color: var(--primary);">{{ p.name }}</h1>
                <p style="font-size: 1.5rem; color: #fff;">${{ p.price }}</p>
                <p>{{ p.description }}</p>
                <p style="color: #888;">Stock: {{ p.stock }} units</p>
                
                <form action="/api/cart/add" method="POST" style="margin-top: 2rem;">
                    <!-- Note: Keeping API for cart add for now, or could make form submit to special route -->
                    <!-- Let's make it a button that sends JSON or a form that accepts standard POST -->
                    <div class="form-group">
                        <label>Quantity</label>
                        <input type="number" name="quantity" value="1" class="form-control" style="width: 100px;">
                    </div>
                    <input type="hidden" name="product_id" value="{{ p.id }}">
                    <button type="submit" class="btn">Add to Encryption Layer (Cart)</button>
                </form>
            </div>
        </div>
        {% endblock %}
        """.replace('{% extends "layout" %}', HTML_TEMPLATE)
        return render_template_string(detail_html, p=product)
    return "Product not found", 404

# ============================================================================
# SHOPPING CART & CHECKOUT
# ============================================================================

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add to cart - VULN: Negative quantity"""
    data = request.json
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    session['cart'][str(product_id)] = session['cart'].get(str(product_id), 0) + quantity
    session.modified = True
    
    if quantity < 0:
        return jsonify({'message': 'Item added to cart', 'vuln': 'Business Logic Flaw - Negative Quantity', 'cart': session['cart']})
    
    return jsonify({'message': 'Item added', 'cart': session['cart']})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Checkout - VULN: Race condition, Price manipulation, Coupon abuse"""
    data = request.json
    user_id = data.get('user_id')
    coupon_code = data.get('coupon_code', '')
    items = data.get('items', [])
    
    conn = get_db()
    total = sum(item['price'] * item['quantity'] for item in items)
    
    if coupon_code:
        coupon = conn.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,)).fetchone()
        if coupon:
            discount = coupon['discount']
            total -= discount
            conn.execute('UPDATE coupons SET used_count = used_count + 1 WHERE code = ?', (coupon_code,))
    
    for item in items:
        product = conn.execute('SELECT stock FROM products WHERE id = ?', (item['product_id'],)).fetchone()
        if product and product['stock'] >= item['quantity']:
            conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?', 
                        (item['quantity'], item['product_id']))
    
    conn.execute('INSERT INTO orders (user_id, total, coupon_code, status) VALUES (?, ?, ?, ?)',
                (user_id, total, coupon_code, 'completed'))
    order_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    for item in items:
        conn.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                    (order_id, item['product_id'], item['quantity'], item['price']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Order placed successfully', 'order_id': order_id, 'total': total, 'vuln': 'Price Manipulation + Race Condition + Coupon Abuse'})

# ============================================================================
# ORDERS
# ============================================================================

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order - VULN: IDOR"""
    conn = get_db()
    order = conn.execute(f"SELECT * FROM orders WHERE id = {order_id}").fetchone()
    
    if order:
        items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
        conn.close()
        return jsonify({'order': dict(order), 'items': [dict(i) for i in items], 'vuln': 'IDOR'})
    
    conn.close()
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/orders/user/<user_id>', methods=['GET'])
def get_user_orders(user_id):
    """Get user orders - VULN: IDOR"""
    conn = get_db()
    orders = conn.execute(f"SELECT * FROM orders WHERE user_id = {user_id}").fetchall()
    conn.close()
    return jsonify({'orders': [dict(o) for o in orders], 'vuln': 'IDOR'})

# ============================================================================
# PAYMENT
# ============================================================================

@app.route('/api/payment/process', methods=['POST'])
def process_payment():
    """Process payment - VULN: Payment bypass"""
    data = request.json
    amount = float(data.get('amount', 0))
    payment_method = data.get('payment_method', 'credit_card')
    
    if amount <= 0:
        return jsonify({'message': 'Payment processed successfully', 'amount': amount, 'vuln': 'Payment Bypass - Zero/Negative Amount'})
    
    return jsonify({'message': 'Payment processed', 'amount': amount, 'method': payment_method})

# ============================================================================
# ADMIN
# ============================================================================

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    """Admin users - VULN: Broken Access Control"""
    conn = get_db()
    users = conn.execute('SELECT id, username, email, role, balance FROM users').fetchall()
    conn.close()
    return jsonify({'users': [dict(u) for u in users], 'vuln': 'Broken Access Control'})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Admin stats - VULN: Information disclosure"""
    conn = get_db()
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_orders': conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
        'total_revenue': conn.execute('SELECT SUM(total) FROM orders').fetchone()[0] or 0,
        'secret_key': app.secret_key,
        'jwt_secret': JWT_SECRET,
        'vuln': 'Information Disclosure'
    }
    conn.close()
    return jsonify(stats)

# ============================================================================
# MISC
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'app': 'E-Commerce Platform'})

@app.route('/')
def index():
    home_html = """
    {% extends "layout" %}
    {% block content %}
    <div class="hero">
        <h1 style="font-size: 4rem; text-shadow: 0 0 20px var(--primary);">CYBERSHOP 2077</h1>
        <p>The premier marketplace for zero-day exploits and high-end neural hardware.</p>
        <br>
        <a href="/products" class="btn" style="padding: 1rem 2rem; font-size: 1.2rem;">ENTER MARKETPLACE</a>
        <br><br>
        <p style="font-size: 0.8rem; color: #555;">SECURE CONNECTION ESTABLISHED. PROTOCOL V2.0 ACTIVE.</p>
    </div>
    {% endblock %}
    """.replace('{% extends "layout" %}', HTML_TEMPLATE)
    return render_template_string(home_html)

if __name__ == '__main__':
    print("=" * 70)
    print("VULNERABLE E-COMMERCE PLATFORM - Research Variant 1")
    print("=" * 70)
    print("  DELIBERATELY VULNERABLE - For Research & Training Only!")
    print("=" * 70)
    print("\nFocus Areas:")
    print("   • Business logic flaws (negative quantities, price manipulation)")
    print("   • Payment vulnerabilities (bypass, zero amount)")
    print("   • Race conditions (checkout, stock, coupons)")
    print("   • API security (IDOR, BAC, mass assignment)")
    print("   • SQL injection in search and filters")
    init_db()
    print("\n Starting on http://localhost:5002\n")
    print("=" * 70)
    app.run(port=5002, debug=True)
