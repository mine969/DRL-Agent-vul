"""
Initialize All Target Databases
================================

This script creates and seeds all 5 target application databases
with sample data for training and testing.
"""

import sqlite3
import hashlib
import os

def init_banking_db():
    """Initialize Banking database"""
    conn = sqlite3.connect('env/banking.db')
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
    print("✓ Banking database initialized")

def init_blog_db():
    """Initialize Blog database"""
    conn = sqlite3.connect('env/blog.db')
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
    print("✓ Blog database initialized")

def init_ecommerce_db():
    """Initialize E-Commerce database"""
    conn = sqlite3.connect('env/ecommerce.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'customer',
        balance REAL DEFAULT 100.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        stock INTEGER,
        category TEXT,
        image_url TEXT
    )''')
    
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', 'admin@shop.com', hashlib.md5(b'admin123').hexdigest(), 'admin', 10000.0),
            ('customer', 'customer@shop.com', hashlib.md5(b'password').hexdigest(), 'customer', 100.0),
        ]
        c.executemany('INSERT INTO users (username, email, password, role, balance) VALUES (?, ?, ?, ?, ?)', users)
        
        products = [
            ('Laptop Pro', 'High-performance laptop', 999.99, 50, 'Electronics', 'laptop.jpg'),
            ('Smartphone X', 'Latest smartphone', 699.99, 100, 'Electronics', 'phone.jpg'),
        ]
        c.executemany('INSERT INTO products (name, description, price, stock, category, image_url) VALUES (?, ?, ?, ?, ?, ?)', products)
    
    conn.commit()
    conn.close()
    print("✓ E-Commerce database initialized")

def init_social_db():
    """Initialize Social Media database"""
    conn = sqlite3.connect('env/social.db')
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
    
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', 'admin@social.com', hashlib.md5(b'admin123').hexdigest(), 'Admin user', 'admin.jpg', 0),
            ('alice', 'alice@social.com', hashlib.md5(b'password').hexdigest(), 'Hello world!', 'alice.jpg', 0),
        ]
        c.executemany('INSERT INTO users (username, email, password, bio, avatar, is_private) VALUES (?, ?, ?, ?, ?, ?)', users)
        
        posts = [
            (1, 'Welcome to our social platform!', None, 10),
            (2, 'Just joined! Excited to be here.', None, 5),
        ]
        c.executemany('INSERT INTO posts (user_id, content, image_url, likes) VALUES (?, ?, ?, ?)', posts)
    
    conn.commit()
    conn.close()
    print("✓ Social Media database initialized")

def init_fileshare_db():
    """Initialize FileShare database"""
    conn = sqlite3.connect('env/fileshare.db')
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
    print("✓ FileShare database initialized")

if __name__ == '__main__':
    print("=" * 70)
    print("🗄️  INITIALIZING ALL TARGET DATABASES")
    print("=" * 70)
    print()
    
    # Ensure env directory exists
    os.makedirs('env', exist_ok=True)
    
    # Initialize all databases
    init_banking_db()
    init_blog_db()
    init_ecommerce_db()
    init_social_db()
    init_fileshare_db()
    
    print()
    print("=" * 70)
    print("✅ ALL DATABASES INITIALIZED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("📁 Database files created in env/ folder:")
    print("   • env/banking.db")
    print("   • env/blog.db")
    print("   • env/ecommerce.db")
    print("   • env/social.db")
    print("   • env/fileshare.db")
    print()
    print("🚀 Ready to start training!")
    print("   Run: python train_multi_target.py --episodes 1000")
