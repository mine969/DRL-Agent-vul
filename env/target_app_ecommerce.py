"""
🛒 VULNERABLE E-COMMERCE PLATFORM - Research Variant 1
=======================================================

A deliberately vulnerable e-commerce application for AI security training.
Focus: Business logic flaws, payment vulnerabilities, API security

⚠️ DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, jsonify, session
import sqlite3
import hashlib
import datetime
import jwt
import sys
import io

# Force UTF-8 encoding for Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


app = Flask(__name__)
app.secret_key = 'ecommerce_secret_2025'
JWT_SECRET = 'ecommerce_jwt_secret'
DB_NAME = 'ecommerce.db'

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

@app.route('/api/register', methods=['POST'])
def register():
    """User registration - VULN: Mass assignment"""
    data = request.json
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
        return jsonify({'message': 'User registered', 'vuln': 'Mass Assignment'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Login - VULN: SQL Injection"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = get_db()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashlib.md5(password.encode()).hexdigest()}'"
    
    try:
        user = conn.execute(query).fetchone()
        if user:
            token = jwt.encode({
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({'token': token, 'user': dict(user), 'message': 'Login successful'})
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e), 'vuln': 'SQL Injection'}), 500
    finally:
        conn.close()

# ============================================================================
# PRODUCTS
# ============================================================================

@app.route('/api/products', methods=['GET'])
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
        return jsonify({'products': [dict(p) for p in products]})
    except Exception as e:
        return jsonify({'error': str(e), 'vuln': 'SQL Injection'}), 500
    finally:
        conn.close()

@app.route('/api/products/<product_id>', methods=['GET', 'PUT'])
def product_detail(product_id):
    """Product detail - VULN: IDOR, Price manipulation"""
    conn = get_db()
    
    if request.method == 'GET':
        product = conn.execute(f"SELECT * FROM products WHERE id = {product_id}").fetchone()
        conn.close()
        return jsonify(dict(product)) if product else ('', 404)
    
    elif request.method == 'PUT':
        data = request.json
        conn.execute('UPDATE products SET price = ?, stock = ? WHERE id = ?',
                    (data.get('price'), data.get('stock'), product_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Product updated', 'vuln': 'Missing Authorization'})

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
    return jsonify({
        'message': 'E-Commerce API',
        'endpoints': ['/api/register', '/api/login', '/api/products', '/api/cart/add', '/api/checkout', '/api/orders/<id>', '/api/payment/process', '/api/admin/users']
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🛒 VULNERABLE E-COMMERCE PLATFORM - Research Variant 1")
    print("=" * 70)
    print("⚠️  DELIBERATELY VULNERABLE - For Research & Training Only!")
    print("=" * 70)
    print("\n📋 Focus Areas:")
    print("   • Business logic flaws (negative quantities, price manipulation)")
    print("   • Payment vulnerabilities (bypass, zero amount)")
    print("   • Race conditions (checkout, stock, coupons)")
    print("   • API security (IDOR, BAC, mass assignment)")
    print("   • SQL injection in search and filters")
    init_db()
    print("\n🚀 Starting on http://localhost:5002\n")
    print("=" * 70)
    app.run(port=5002, debug=True)
