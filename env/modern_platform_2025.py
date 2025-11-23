"""
🚀 MODERN 2025 SOCIAL PLATFORM - AI Training Environment
=========================================================

A realistic, modern web application combining:
- Social Media (posts, likes, follows)
- E-commerce (products, cart, payments)
- SaaS Features (subscriptions, API keys)
- Real-time Features (notifications, chat)
- Cloud Integration (file uploads, webhooks)

⚠️ DELIBERATELY VULNERABLE - For AI Security Training Only!
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify, make_response, send_file
import sqlite3
import jwt
import datetime
import hashlib
import os
import random
import string
import time
import pickle
import base64
from functools import wraps

app = Flask(__name__)
app.secret_key = 'modern_platform_2025_secret'
JWT_SECRET = 'jwt_secret_2025'

# ============================================================================
# DATABASE SETUP - Modern Schema
# ============================================================================

def init_db():
    conn = sqlite3.connect('modern_platform.db')
    c = conn.cursor()
    
    # Users table with modern fields
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        bio TEXT,
        avatar_url TEXT,
        verified BOOLEAN DEFAULT 0,
        subscription_tier TEXT DEFAULT 'free',
        api_key TEXT,
        balance REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Posts table (social media)
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        image_url TEXT,
        likes INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Products table (e-commerce)
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        stock INTEGER,
        category TEXT,
        image_url TEXT,
        seller_id INTEGER,
        FOREIGN KEY(seller_id) REFERENCES users(id)
    )''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    
    # Messages table (chat)
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        content TEXT,
        read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(from_user_id) REFERENCES users(id),
        FOREIGN KEY(to_user_id) REFERENCES users(id)
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        content TEXT,
        read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Seed data
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        print("🌱 Seeding modern platform database...")
        
        # Create users
        users = [
            ('admin', 'admin@platform.com', 'admin123', 'admin', 'Platform Administrator', 'https://i.pravatar.cc/150?img=1', 1, 'premium', 'sk_live_admin_key_123', 10000.0),
            ('alice', 'alice@example.com', 'password', 'user', 'Tech enthusiast 🚀', 'https://i.pravatar.cc/150?img=2', 1, 'pro', 'sk_live_alice_key_456', 500.0),
            ('bob', 'bob@example.com', 'password', 'user', 'Developer & Designer', 'https://i.pravatar.cc/150?img=3', 0, 'free', 'sk_test_bob_key_789', 50.0),
            ('seller', 'seller@shop.com', 'password', 'seller', 'Official Store', 'https://i.pravatar.cc/150?img=4', 1, 'business', 'sk_live_seller_key_999', 5000.0)
        ]
        
        for user in users:
            c.execute("""INSERT INTO users (username, email, password, role, bio, avatar_url, verified, 
                        subscription_tier, api_key, balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", user)
        
        # Create posts
        posts = [
            (1, 'Welcome to our modern platform! 🎉 #launch', 'https://picsum.photos/600/400?random=1', 42, 12),
            (2, 'Just deployed my new AI project! Check it out 🤖', 'https://picsum.photos/600/400?random=2', 28, 5),
            (3, 'Beautiful sunset today 🌅', 'https://picsum.photos/600/400?random=3', 156, 23),
            (4, 'New products available in our store! 🛍️', 'https://picsum.photos/600/400?random=4', 89, 15)
        ]
        
        for post in posts:
            c.execute("INSERT INTO posts (user_id, content, image_url, likes, shares) VALUES (?, ?, ?, ?, ?)", post)
        
        # Create products
        products = [
            ('Premium AI Course', 'Learn AI & Machine Learning', 299.99, 50, 'Education', 'https://picsum.photos/300/300?random=5', 4),
            ('Smart Watch Pro', 'Latest smartwatch technology', 399.99, 100, 'Electronics', 'https://picsum.photos/300/300?random=6', 4),
            ('Coding Bootcamp', 'Full-stack development course', 499.99, 30, 'Education', 'https://picsum.photos/300/300?random=7', 4),
            ('Designer Headphones', 'Premium audio experience', 199.99, 75, 'Electronics', 'https://picsum.photos/300/300?random=8', 4)
        ]
        
        for product in products:
            c.execute("""INSERT INTO products (name, description, price, stock, category, image_url, seller_id) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", product)
        
        print("✅ Database seeded successfully!")
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('modern_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

init_db()

# ============================================================================
# MODERN HOMEPAGE - 2025 Trending Design
# ============================================================================

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModernHub - Social Platform 2025</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .card ul {
            list-style: none;
            padding: 0;
        }
        .card li {
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .card li:last-child {
            border-bottom: none;
        }
        .card a {
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s;
        }
        .card a:hover {
            color: #764ba2;
        }
        .badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-left: 10px;
        }
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 ModernHub Platform</h1>
            <p class="subtitle">Next-Gen Social Platform with E-commerce & SaaS Features</p>
        </header>
        
        <div class="warning">
            <strong>⚠️ Training Environment:</strong> This is a deliberately vulnerable application for AI security training. Never deploy in production!
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>👥 Social Features</h3>
                <ul>
                    <li><a href="/feed">📱 Social Feed</a></li>
                    <li><a href="/profile/1">👤 User Profiles</a></li>
                    <li><a href="/messages">💬 Direct Messages</a></li>
                    <li><a href="/notifications">🔔 Notifications</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>🛍️ E-commerce</h3>
                <ul>
                    <li><a href="/shop">🏪 Product Shop</a></li>
                    <li><a href="/cart">🛒 Shopping Cart</a></li>
                    <li><a href="/orders">📦 My Orders</a></li>
                    <li><a href="/checkout">💳 Checkout</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>🔧 SaaS & API</h3>
                <ul>
                    <li><a href="/dashboard">📊 Dashboard</a></li>
                    <li><a href="/api/docs">📚 API Documentation</a></li>
                    <li><a href="/webhooks">🔗 Webhooks</a></li>
                    <li><a href="/subscription">💎 Subscription Plans</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>🔐 Authentication</h3>
                <ul>
                    <li><a href="/login">🔑 Login</a></li>
                    <li><a href="/register">📝 Register</a></li>
                    <li><a href="/oauth">🌐 OAuth Login</a></li>
                    <li><a href="/api/token">🎫 Get API Token</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>📁 File Management</h3>
                <ul>
                    <li><a href="/upload">📤 Upload Files</a></li>
                    <li><a href="/files">📂 My Files</a></li>
                    <li><a href="/share">🔗 Share Files</a></li>
                    <li><a href="/cdn">🌐 CDN Assets</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>⚙️ Admin & Settings</h3>
                <ul>
                    <li><a href="/admin">👑 Admin Panel</a></li>
                    <li><a href="/settings">⚙️ User Settings</a></li>
                    <li><a href="/analytics">📈 Analytics</a></li>
                    <li><a href="/logs">📋 System Logs</a></li>
                </ul>
            </div>
        </div>
        
        <div class="card" style="margin-top: 30px;">
            <h3>🎯 Vulnerability Coverage</h3>
            <p><span class="badge">OWASP Top 10 2025</span> <span class="badge">50+ Endpoints</span> <span class="badge">25+ Vuln Types</span></p>
            <p style="margin-top: 15px; color: #666;">
                Includes: SQL Injection, XSS, CSRF, IDOR, SSRF, XXE, Deserialization, Business Logic Flaws, 
                API Vulnerabilities, File Inclusion, Authentication Bypass, and more!
            </p>
        </div>
    </div>
</body>
</html>
    ''')

# ============================================================================
# Continue with all the vulnerable endpoints...
# (I'll add them in the next part to keep this organized)
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 MODERNHUB PLATFORM 2025 - AI Training Environment")
    print("=" * 70)
    print("⚠️  DELIBERATELY VULNERABLE - For Training Only!")
    print("=" * 70)
    print("\n✨ Features:")
    print("   • Modern 2025 UI/UX")
    print("   • Social Media Platform")
    print("   • E-commerce Integration")
    print("   • SaaS & API Features")
    print("   • Real-time Capabilities")
    print("   • 50+ Vulnerable Endpoints")
    print("   • 25+ Attack Vectors")
    print("\n🚀 Starting on http://localhost:5000\n")
    print("=" * 70)
    app.run(port=5000, debug=True)
