"""
 VULNERABLE SOCIAL MEDIA PLATFORM - Research Variant 2
=========================================================

A deliberately vulnerable social media application for AI security training.
Focus: XSS, authentication, file uploads, IDOR

 DELIBERATELY VULNERABLE - For Research & Training Only!
"""

from flask import Flask, request, jsonify, session, send_from_directory, render_template_string, redirect, url_for
import sqlite3
import hashlib
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'social_secret_2025'
DB_NAME = 'env/social.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# MODERN UI TEMPLATES
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ConnectHub - Social Network</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #1DA1F2;
            --primary-hover: #1a91da;
            --bg: #000000;
            --card-bg: #16181C;
            --hover-bg: #1E1F23;
            --text-main: #E7E9EA;
            --text-muted: #71767A;
            --border: #2F3336;
            --success: #00BA7C;
            --error: #F4212E;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
        }
        /* Sidebar Navigation */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 275px;
            height: 100vh;
            padding: 20px 16px;
            border-right: 1px solid var(--border);
            overflow-y: auto;
        }
        .logo {
            font-size: 28px;
            font-weight: 700;
            color: var(--text-main);
            text-decoration: none;
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 20px;
        }
        .logo:hover { background: var(--hover-bg); border-radius: 30px; }
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--text-main);
            text-decoration: none;
            font-size: 20px;
            font-weight: 500;
            border-radius: 30px;
            margin-bottom: 4px;
            transition: background 0.2s;
        }
        .nav-item:hover { background: var(--hover-bg); }
        .nav-item.active { font-weight: 700; }
        .nav-item svg { width: 26px; height: 26px; margin-right: 20px; }
        .nav-icon { width: 26px; height: 26px; margin-right: 20px; display: inline-block; }
        
        /* Main Content */
        .main-container {
            margin-left: 275px;
            display: flex;
            min-height: 100vh;
        }
        .feed-column {
            flex: 1;
            max-width: 600px;
            border-right: 1px solid var(--border);
            border-left: 1px solid var(--border);
        }
        .sidebar-column {
            width: 350px;
            padding: 20px;
        }
        .content-header {
            position: sticky;
            top: 0;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(12px);
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            font-size: 20px;
            font-weight: 700;
            z-index: 10;
        }
        
        /* Post Composer */
        .post-composer {
            padding: 16px;
            border-bottom: 1px solid var(--border);
        }
        .composer-input {
            width: 100%;
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 20px;
            padding: 12px 0;
            resize: none;
            min-height: 60px;
            font-family: inherit;
        }
        .composer-input:focus { outline: none; }
        .composer-input::placeholder { color: var(--text-muted); }
        .composer-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--border);
        }
        .composer-icons { display: flex; gap: 16px; }
        .icon-btn {
            color: var(--primary);
            background: none;
            border: none;
            cursor: pointer;
            padding: 8px;
            border-radius: 20px;
            transition: background 0.2s;
        }
        .icon-btn:hover { background: rgba(29, 161, 242, 0.1); }
        
        /* Post Cards */
        .post-card {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            transition: background 0.2s;
        }
        .post-card:hover { background: var(--hover-bg); }
        .post-header {
            display: flex;
            gap: 12px;
            margin-bottom: 4px;
        }
        .avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 18px;
        }
        .post-info {
            flex: 1;
            min-width: 0;
        }
        .post-author {
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 700;
            font-size: 15px;
            color: var(--text-main);
            text-decoration: none;
        }
        .post-author:hover { text-decoration: underline; }
        .post-handle {
            color: var(--text-muted);
            font-weight: 400;
            margin-left: 4px;
        }
        .post-time {
            color: var(--text-muted);
            font-size: 15px;
        }
        .post-time::before { content: "· "; }
        .post-content {
            font-size: 15px;
            line-height: 1.5;
            word-wrap: break-word;
            margin: 8px 0;
        }
        .post-image {
            width: 100%;
            border-radius: 16px;
            margin-top: 12px;
            max-height: 500px;
            object-fit: cover;
        }
        .post-actions {
            display: flex;
            justify-content: space-around;
            margin-top: 12px;
            padding-top: 8px;
            max-width: 425px;
        }
        .action-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 13px;
            padding: 8px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .action-btn:hover { background: rgba(29, 161, 242, 0.1); color: var(--primary); }
        .action-btn.liked { color: var(--error); }
        .action-btn.comment:hover { background: rgba(0, 186, 124, 0.1); color: var(--success); }
        .action-icon { width: 18px; height: 18px; }
        
        /* Buttons */
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: var(--primary-hover); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-outline {
            background: transparent;
            border: 2px solid var(--border);
            color: var(--text-main);
        }
        .btn-outline:hover { background: var(--hover-bg); border-color: var(--primary); }
        .btn-sm {
            padding: 8px 16px;
            font-size: 14px;
        }
        
        /* Sidebar Widgets */
        .widget {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .widget-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
        }
        .trend-item {
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
        }
        .trend-item:last-child { border-bottom: none; }
        .trend-item:hover { background: var(--hover-bg); margin: 0 -16px; padding: 12px 16px; }
        .trend-category {
            font-size: 13px;
            color: var(--text-muted);
        }
        .trend-name {
            font-weight: 700;
            font-size: 15px;
            margin-top: 2px;
        }
        .trend-count {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        
        /* Profile */
        .profile-header {
            position: relative;
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .profile-avatar {
            position: absolute;
            bottom: -60px;
            left: 20px;
            width: 130px;
            height: 130px;
            border-radius: 50%;
            border: 4px solid var(--bg);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .profile-info {
            padding: 80px 20px 20px;
        }
        .profile-actions {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            margin-bottom: 20px;
        }
        .profile-stats {
            display: flex;
            gap: 24px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }
        .stat {
            cursor: pointer;
        }
        .stat:hover .stat-label { text-decoration: underline; }
        .stat-number {
            font-weight: 700;
            font-size: 20px;
        }
        .stat-label {
            color: var(--text-muted);
            font-size: 15px;
        }
        
        /* Forms */
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 15px;
        }
        .form-control {
            width: 100%;
            padding: 12px 16px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-main);
            font-size: 15px;
            font-family: inherit;
        }
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        /* Alert */
        .alert {
            padding: 16px;
            border-radius: 16px;
            margin-bottom: 16px;
            background: rgba(244, 33, 46, 0.1);
            border: 1px solid var(--error);
            color: var(--error);
        }
        .alert-success {
            background: rgba(0, 186, 124, 0.1);
            border-color: var(--success);
            color: var(--success);
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="/posts" class="logo">🐦 ConnectHub</a>
        <a href="/posts" class="nav-item {% if request.path == '/posts' or request.path == '/' %}active{% endif %}">
            <span class="nav-icon">🏠</span> Home
        </a>
        {% if session.user_id %}
            <a href="/search" class="nav-item {% if '/search' in request.path %}active{% endif %}">
                <span class="nav-icon">🔍</span> Explore
            </a>
            <a href="/messages/{{ session.user_id }}" class="nav-item {% if '/messages' in request.path %}active{% endif %}">
                <span class="nav-icon">💬</span> Messages
            </a>
            <a href="/profile/{{ session.user_id }}" class="nav-item {% if '/profile' in request.path %}active{% endif %}">
                <span class="nav-icon">👤</span> Profile
            </a>
            <a href="/logout" class="nav-item">
                <span class="nav-icon">🚪</span> Logout
            </a>
        {% else %}
            <a href="/login" class="nav-item">
                <span class="nav-icon">🔑</span> Login
            </a>
            <a href="/register" class="nav-item">
                <span class="nav-icon">✨</span> Join
            </a>
        {% endif %}
    </div>
    
    <div class="main-container">
        <div class="feed-column">
            <div class="content-header">
                {% block header %}Home{% endblock %}
            </div>
            {% if error %}<div class="alert">{{ error }}</div>{% endif %}
            {% block content %}{% endblock %}
        </div>
        <div class="sidebar-column">
            {% block sidebar %}
            <div class="widget">
                <div class="widget-title">Trending</div>
                <div class="trend-item">
                    <div class="trend-category">Technology · Trending</div>
                    <div class="trend-name">AI & Machine Learning</div>
                    <div class="trend-count">12.5K posts</div>
                </div>
                <div class="trend-item">
                    <div class="trend-category">Entertainment · Trending</div>
                    <div class="trend-name">New Movie Releases</div>
                    <div class="trend-count">8.2K posts</div>
                </div>
                <div class="trend-item">
                    <div class="trend-category">Sports · Trending</div>
                    <div class="trend-name">Championship Finals</div>
                    <div class="trend-count">15.3K posts</div>
                </div>
            </div>
            {% endblock %}
        </div>
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        content TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS friendships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        friend_id INTEGER,
        status TEXT DEFAULT 'pending'
    )''')
    
    # Seed data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Create diverse user profiles
        users = [
            ('admin', 'admin@social.com', hashlib.md5(b'admin123').hexdigest(), 'Platform Administrator', 'admin.jpg', 0),
            ('tech_guru', 'tech@email.com', hashlib.md5(b'password').hexdigest(), 'Software Engineer | AI Enthusiast | Coffee Addict ☕', 'tech.jpg', 0),
            ('travel_nomad', 'travel@email.com', hashlib.md5(b'password').hexdigest(), 'Digital Nomad 🌍 | 47 countries and counting', 'travel.jpg', 0),
            ('fitness_coach', 'fitness@email.com', hashlib.md5(b'password').hexdigest(), 'Personal Trainer | Nutrition Expert | Marathon Runner', 'fitness.jpg', 0),
            ('foodie_jane', 'foodie@email.com', hashlib.md5(b'password').hexdigest(), 'Food Blogger | Recipe Creator | Michelin Star Hunter', 'foodie.jpg', 0),
            ('photo_pro', 'photo@email.com', hashlib.md5(b'password').hexdigest(), 'Professional Photographer | Nature Lover 📸', 'photo.jpg', 0),
            ('music_beats', 'music@email.com', hashlib.md5(b'password').hexdigest(), 'DJ | Music Producer | Festival Junkie 🎵', 'music.jpg', 0),
            ('book_worm', 'books@email.com', hashlib.md5(b'password').hexdigest(), 'Avid Reader | Book Reviewer | Library Enthusiast', 'books.jpg', 0),
            ('gamer_pro', 'gamer@email.com', hashlib.md5(b'password').hexdigest(), 'Pro Gamer | Streamer | Esports Competitor 🎮', 'gamer.jpg', 0),
            ('art_creator', 'art@email.com', hashlib.md5(b'password').hexdigest(), 'Digital Artist | Illustrator | NFT Creator', 'art.jpg', 0),
            ('startup_founder', 'startup@email.com', hashlib.md5(b'password').hexdigest(), 'Entrepreneur | Tech Startup Founder | Angel Investor', 'startup.jpg', 0),
            ('yoga_master', 'yoga@email.com', hashlib.md5(b'password').hexdigest(), 'Yoga Instructor | Mindfulness Coach | Wellness Advocate', 'yoga.jpg', 0),
            ('crypto_trader', 'crypto@email.com', hashlib.md5(b'password').hexdigest(), 'Crypto Enthusiast | Blockchain Developer | HODL 🚀', 'crypto.jpg', 0),
            ('fashion_style', 'fashion@email.com', hashlib.md5(b'password').hexdigest(), 'Fashion Designer | Style Influencer | Runway Model', 'fashion.jpg', 0),
            ('science_nerd', 'science@email.com', hashlib.md5(b'password').hexdigest(), 'Physicist | Science Communicator | Space Geek 🔬', 'science.jpg', 0),
            ('pet_lover', 'pets@email.com', hashlib.md5(b'password').hexdigest(), 'Animal Rescuer | Dog Mom | Cat Dad 🐾', 'pets.jpg', 0),
            ('comedy_king', 'comedy@email.com', hashlib.md5(b'password').hexdigest(), 'Stand-up Comedian | Meme Lord | Laughter Therapist 😂', 'comedy.jpg', 0),
            ('eco_warrior', 'eco@email.com', hashlib.md5(b'password').hexdigest(), 'Environmental Activist | Sustainability Advocate | Zero Waste', 'eco.jpg', 1)
        ]
        c.executemany('INSERT INTO users (username, email, password, bio, avatar, is_private) VALUES (?, ?, ?, ?, ?, ?)', users)
        
        # Create diverse posts
        posts = [
            (1, 'Welcome to SocialNet! Excited to connect with all of you. 🎉', None, 25),
            (2, 'Just deployed my new AI project! Check it out on GitHub. The future is now! 🤖', 'ai_project.jpg', 42),
            (3, 'Sunset in Bali is absolutely breathtaking. This is why I travel! 🌅', 'bali_sunset.jpg', 89),
            (4, 'New workout routine: 100 push-ups, 100 sit-ups, 100 squats, 10km run. Every. Single. Day. 💪', None, 67),
            (5, 'Made the perfect carbonara today! Recipe in comments 👇', 'carbonara.jpg', 103),
            (6, 'Golden hour photography tips: Always shoot during magic hour for that perfect glow ✨', 'golden_hour.jpg', 78),
            (7, 'New track dropping this Friday! Been working on this for months 🎶', 'studio.jpg', 156),
            (8, 'Just finished "The Midnight Library". Absolutely mind-blowing! 📚', None, 45),
            (9, 'Won the championship! GG to all competitors. Practice makes perfect 🏆', 'trophy.jpg', 234),
            (10, 'New digital art piece: "Cyber Dreams". Available as NFT! 🎨', 'cyber_art.jpg', 91),
            (11, 'Our startup just hit 10K users! Thank you all for the support! 🚀', None, 187),
            (12, 'Morning meditation session complete. Start your day with mindfulness 🧘', 'meditation.jpg', 56),
            (13, 'Bitcoin just hit a new ATH! Time to HODL stronger 📈', None, 298),
            (14, 'Paris Fashion Week was incredible! So many amazing designs 👗', 'fashion_week.jpg', 145),
            (15, 'Explaining quantum entanglement in simple terms: Imagine two particles... 🔬', None, 72),
            (16, 'Adopted a new rescue puppy today! Meet Max! 🐕', 'puppy.jpg', 412),
            (17, 'Why did the programmer quit his job? Because he didn\'t get arrays! 😂', None, 189),
            (18, 'Planted 100 trees today with the community. Every action counts! 🌳', 'tree_planting.jpg', 167),
            (2, 'Working on a new machine learning model. The accuracy is insane! 🧠', None, 38),
            (3, 'Exploring the temples of Angkor Wat. History comes alive here! 🏛️', 'angkor.jpg', 95),
            (4, 'Rest days are just as important as training days. Listen to your body! 💯', None, 54),
            (5, 'Trying out molecular gastronomy. Science meets cooking! 🧪', 'molecular.jpg', 76),
            (6, 'Captured the Milky Way last night. Long exposure magic! 🌌', 'milky_way.jpg', 201),
            (7, 'Collaboration with @tech_guru on a new electronic track! Coming soon 🎧', None, 112),
            (8, 'Book club meeting tonight! We\'re discussing dystopian fiction 📖', None, 34),
            (9, 'Streaming live in 30 minutes! Come hang out! 🎮', None, 87),
            (10, 'Commission work finished! DM me for custom art requests ✏️', 'commission.jpg', 63),
            (11, 'Pitch deck tips for startups: Keep it simple, focus on the problem 💼', None, 94),
            (12, 'New yoga flow for beginners. Link in bio! 🙏', 'yoga_flow.jpg', 128),
            (13, 'Ethereum 2.0 is a game changer. Here\'s why... 🔗', None, 156),
            (14, 'Sustainable fashion is the future. Shop consciously! ♻️', None, 89),
            (15, 'Just published a new paper on dark matter. Peer review time! 📝', None, 47),
            (16, 'Cat vs Dog debate: Why not both? 🐱🐶', 'cat_dog.jpg', 276),
            (17, 'New stand-up special coming to Netflix next month! 🎤', None, 198),
            (18, 'Zero waste challenge: Day 30! Here\'s what I learned... 🌍', 'zero_waste.jpg', 143),
            (2, 'Code review best practices: Always be kind and constructive 👨‍💻', None, 52),
            (3, 'Scuba diving in the Great Barrier Reef tomorrow! 🤿', None, 71),
            (4, 'Meal prep Sunday! Consistency is key to fitness goals 🥗', 'meal_prep.jpg', 98),
            (5, 'Homemade sourdough bread. The patience was worth it! 🍞', 'sourdough.jpg', 134),
            (6, 'Photography workshop this weekend. Limited spots available! 📷', None, 45),
            (7, 'Behind the scenes of my latest music video 🎬', 'bts_video.jpg', 167),
            (8, 'Reading challenge update: 42 books down, 8 to go! 📚', None, 39),
            (9, 'New gaming setup reveal! RGB everything! 💻', 'gaming_setup.jpg', 223),
            (10, 'Art tutorial: How to draw realistic eyes 👁️', None, 87)
        ]
        c.executemany('INSERT INTO posts (user_id, content, image_url, likes) VALUES (?, ?, ?, ?)', posts)
        
        # Create comments
        comments = [
            (1, 2, 'Welcome! Great to have you here!'),
            (2, 1, 'Congrats on the launch! 🎉'),
            (5, 2, 'This looks amazing! Can\'t wait to try it'),
            (3, 3, 'Bali is on my bucket list! 😍'),
            (6, 3, 'Stunning shot! What camera did you use?'),
            (4, 4, 'One Punch Man workout! Respect! 💪'),
            (12, 4, 'Don\'t forget to stretch!'),
            (2, 5, 'Recipe please! 🙏'),
            (5, 5, 'Eggs, pasta, guanciale, pecorino, black pepper. That\'s it!'),
            (6, 6, 'Great tip! I always forget about golden hour'),
            (7, 7, 'Can\'t wait! Your last track was fire 🔥'),
            (8, 8, 'Added to my reading list!'),
            (9, 9, 'Congrats champ! Well deserved!'),
            (10, 10, 'This is incredible! Bidding now'),
            (2, 11, 'Congrats on the milestone!'),
            (12, 12, 'Meditation changed my life'),
            (13, 13, 'To the moon! 🚀'),
            (14, 14, 'Your outfit was my favorite!'),
            (15, 15, 'Finally someone explains it clearly!'),
            (16, 16, 'Max is adorable! 😍'),
            (17, 17, 'LOL! Good one! 😂'),
            (18, 18, 'This is amazing! How can I help?'),
            (3, 19, 'What framework are you using?'),
            (4, 20, 'Angkor Wat is magical!'),
            (5, 21, 'Recovery is crucial!'),
            (6, 22, 'This is so cool! 🧪'),
            (7, 23, 'Wow! What settings?'),
            (8, 24, 'Love collabs! 🎵'),
            (9, 25, 'Count me in!'),
            (10, 26, 'I\'ll be there!'),
            (11, 27, 'Your art is amazing!'),
            (12, 28, 'Great advice!'),
            (13, 29, 'Trying this tomorrow!'),
            (14, 30, 'Exactly! ETH is the future'),
            (15, 31, 'More people need to hear this'),
            (16, 32, 'Congrats on the publication!'),
            (17, 33, 'Team both! 🐾'),
            (18, 34, 'Can\'t wait to watch!'),
            (2, 35, 'Inspiring journey!'),
            (3, 36, 'Code reviews make us better'),
            (4, 37, 'Have fun! Be safe!'),
            (5, 38, 'Meal prep gang! 💪'),
            (6, 39, 'Sourdough is an art form'),
            (7, 40, 'Signing up now!'),
            (8, 41, 'Looks epic!'),
            (9, 42, 'You\'re crushing it!'),
            (10, 43, 'RGB = +10 FPS 😂'),
            (2, 44, 'Very helpful tutorial!')
        ]
        c.executemany('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)', comments)
        
        # Create friendships
        friendships = [
            (2, 3, 'accepted'), (2, 4, 'accepted'), (2, 11, 'accepted'),
            (3, 4, 'accepted'), (3, 6, 'accepted'), (3, 18, 'accepted'),
            (4, 5, 'accepted'), (4, 12, 'accepted'),
            (5, 6, 'accepted'), (5, 16, 'accepted'),
            (6, 7, 'accepted'), (6, 10, 'accepted'),
            (7, 8, 'accepted'), (7, 9, 'accepted'),
            (8, 9, 'accepted'), (8, 15, 'accepted'),
            (9, 10, 'accepted'), (9, 17, 'accepted'),
            (10, 11, 'accepted'), (10, 14, 'accepted'),
            (11, 12, 'accepted'), (11, 13, 'accepted'),
            (12, 13, 'accepted'), (12, 18, 'accepted'),
            (13, 14, 'accepted'), (13, 15, 'accepted'),
            (14, 15, 'accepted'), (14, 16, 'accepted'),
            (15, 16, 'accepted'), (16, 17, 'accepted'),
            (17, 18, 'accepted'),
            (2, 5, 'pending'), (3, 7, 'pending'), (4, 9, 'pending')
        ]
        c.executemany('INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, ?)', friendships)
    
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
    """User registration - VULN: Weak password validation"""
    if request.method == 'GET':
        page_content = """
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <h2 style="text-align: center; color: var(--primary);">Join SocialNet</h2>
            <form method="POST" action="/register">
                <input type="text" name="username" class="form-control" placeholder="Username" required>
                <input type="email" name="email" class="form-control" placeholder="Email" required>
                <input type="password" name="password" class="form-control" placeholder="Password" required>
                <button type="submit" class="btn">Sign Up</button>
            </form>
        </div>
        """
        full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Join ConnectHub').replace('{% block content %}{% endblock %}', page_content)
        return render_template_string(full_html)

    # POST Logic
    data = request.form if request.form else request.json
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashlib.md5(password.encode()).hexdigest()))
        conn.commit()
        return redirect('/login?msg=Welcome! Please login.')
    except Exception as e:
        error_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Sign Up').replace('{% block content %}{% endblock %}', f'<div class="alert">Error: {str(e)}</div>')
        return render_template_string(error_html)
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login - VULN: Session fixation"""
    if request.method == 'GET':
        msg = request.args.get('msg', '')
        page_content = """
        <div class="card" style="max-width: 400px; margin: 0 auto; margin-top: 50px;">
            <h2 style="text-align: center; color: var(--primary);">Login</h2>
            {% if msg %}<div class="alert" style="background: rgba(45, 136, 255, 0.2); color: white;">{{ msg }}</div>{% endif %}
            <form method="POST" action="/login">
                <input type="text" name="username" class="form-control" placeholder="Username" required>
                <input type="password" name="password" class="form-control" placeholder="Password" required>
                <button type="submit" class="btn">Log In</button>
            </form>
        </div>
        """
        full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Log In').replace('{% block content %}{% endblock %}', page_content)
        return render_template_string(full_html, msg=msg)
    
    # POST Logic
    data = request.form if request.form else request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                       (username, hashlib.md5(password.encode()).hexdigest())).fetchone()
    conn.close()
    
    if user:
        # VULN: Session fixation
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/posts')
    
    error_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Log In').replace('{% block content %}{% endblock %}', '<div class="alert">Invalid Credentials</div>')
    return render_template_string(error_html)

@app.route('/api/password-reset', methods=['POST'])
def password_reset():
    """Password reset - VULN: Predictable reset tokens"""
    data = request.json
    email = data.get('email', '')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        # VULN: Predictable token (just user ID)
        reset_token = str(user['id'])
        conn.execute('UPDATE users SET reset_token = ? WHERE id = ?', (reset_token, user['id']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Reset token sent', 'token': reset_token, 'vuln': 'Predictable Reset Token'})
    
    conn.close()
    return jsonify({'error': 'User not found'}), 404

# ============================================================================
# PROFILES
# ============================================================================

@app.route('/profile/<user_id>', methods=['GET'])
def profile(user_id):
    """User profile - VULN: IDOR"""
    conn = get_db()
    
    # VULN: No privacy check - can view private profiles
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return "User not found", 404
    
    # Get user's posts
    user_posts = conn.execute('''SELECT p.*, u.username, u.avatar 
                                 FROM posts p JOIN users u ON p.user_id = u.id 
                                 WHERE p.user_id = ? ORDER BY p.created_at DESC LIMIT 20''', (user_id,)).fetchall()
    
    # Get friend count
    friend_count = conn.execute('SELECT COUNT(*) FROM friendships WHERE user_id = ? AND status = ?', 
                               (user_id, 'accepted')).fetchone()[0]
    
    conn.close()
    
    is_own_profile = session.get('user_id') == user['id']
    
    page_content = """
    <div class="profile-header">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%;"></div>
    </div>
    <div class="profile-info">
        <div class="profile-avatar">
            {{ u.username[0].upper() }}
        </div>
        <div class="profile-actions">
            {% if not is_own_profile %}
            <button class="btn">Follow</button>
            <a href="/messages/{{ u.id }}" class="btn btn-outline" style="text-decoration: none;">Message</a>
            {% else %}
            <a href="/messages/{{ u.id }}" class="btn" style="text-decoration: none;">Messages</a>
            {% endif %}
        </div>
        <h1 style="font-size: 24px; font-weight: 700; margin-bottom: 4px;">{{ u.username }}</h1>
        <p style="color: var(--text-muted); font-size: 15px; margin-bottom: 12px;">@{{ u.username.lower() }}</p>
        {% if u.bio %}
        <p style="font-size: 15px; margin-bottom: 12px; line-height: 1.5;">{{ u.bio }}</p>
        {% endif %}
        <div class="profile-stats">
            <div class="stat">
                <span class="stat-number">{{ posts|length }}</span>
                <span class="stat-label">Posts</span>
            </div>
            <div class="stat">
                <span class="stat-number">{{ friend_count }}</span>
                <span class="stat-label">Following</span>
            </div>
            <div class="stat">
                <span class="stat-number">{{ friend_count }}</span>
                <span class="stat-label">Followers</span>
            </div>
        </div>
    </div>
    
    <div style="border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); display: flex;">
        <a href="#posts" style="flex: 1; text-align: center; padding: 16px; color: var(--text-main); text-decoration: none; font-weight: 600; border-bottom: 2px solid var(--primary);">
            Posts
        </a>
        <a href="#replies" style="flex: 1; text-align: center; padding: 16px; color: var(--text-muted); text-decoration: none; font-weight: 600;">
            Replies
        </a>
        <a href="#media" style="flex: 1; text-align: center; padding: 16px; color: var(--text-muted); text-decoration: none; font-weight: 600;">
            Media
        </a>
    </div>
    
    {% for post in posts %}
    <div class="post-card">
        <div class="post-header">
            <a href="/profile/{{ post.user_id }}" class="avatar" style="text-decoration: none;">
                {{ post.username[0].upper() }}
            </a>
            <div class="post-info">
                <a href="/profile/{{ post.user_id }}" class="post-author">
                    {{ post.username }}
                    <span class="post-handle">@{{ post.username.lower() }}</span>
                </a>
                <div class="post-time">{{ post.created_at }}</div>
            </div>
        </div>
        <div class="post-content">
            {{ post.content | safe }}
        </div>
        {% if post.image_url %}
        <img src="/static/{{ post.image_url }}" class="post-image" alt="Post image">
        {% endif %}
        <div class="post-actions">
            <button class="action-btn comment" onclick="window.location.href='/posts/{{ post.id }}'">
                <span class="action-icon">💬</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">🔄</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">❤️</span>
                <span>{{ post.likes }}</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">📤</span>
            </button>
        </div>
    </div>
    {% endfor %}
    
    {% if not posts %}
    <div style="padding: 60px 20px; text-align: center; color: var(--text-muted);">
        <p style="font-size: 20px; margin-bottom: 8px;">No posts yet</p>
        <p>When {{ u.username }} posts, you'll see it here.</p>
    </div>
    {% endif %}
    """
    
    user_dict = dict(user)
    full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', user_dict['username']).replace('{% block content %}{% endblock %}', page_content)
    return render_template_string(full_html, u=user_dict, posts=[dict(p) for p in user_posts], 
                                 friend_count=friend_count, is_own_profile=is_own_profile)

# ============================================================================
# POSTS
# ============================================================================

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    """Posts - VULN: Stored XSS"""
    conn = get_db()
    
    if request.method == 'GET':
        posts = conn.execute('SELECT p.*, u.username, u.avatar, u.id as user_id FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC LIMIT 50').fetchall()
        conn.close()
        
        page_content = """
        {% if session.user_id %}
        <div class="post-composer">
            <form action="/posts" method="POST" style="display: flex; flex-direction: column;">
                <textarea name="content" class="composer-input" placeholder="What's happening?!" rows="3" required></textarea>
                <div class="composer-actions">
                    <div class="composer-icons">
                        <button type="button" class="icon-btn" title="Media">📷</button>
                        <button type="button" class="icon-btn" title="GIF">🎬</button>
                        <button type="button" class="icon-btn" title="Poll">📊</button>
                        <button type="button" class="icon-btn" title="Emoji">😊</button>
                    </div>
                    <button type="submit" class="btn btn-sm">Post</button>
                </div>
            </form>
        </div>
        {% endif %}
        
        {% for p in posts %}
        <div class="post-card">
            <div class="post-header">
                <a href="/profile/{{ p.user_id }}" class="avatar" style="text-decoration: none;">
                    {{ p.username[0].upper() }}
                </a>
                <div class="post-info">
                    <a href="/profile/{{ p.user_id }}" class="post-author">
                        {{ p.username }}
                        <span class="post-handle">@{{ p.username.lower() }}</span>
                    </a>
                    <div class="post-time">{{ p.created_at }}</div>
                </div>
            </div>
            <div class="post-content">
                {{ p.content | safe }}
            </div>
            {% if p.image_url %}
            <img src="/static/{{ p.image_url }}" class="post-image" alt="Post image">
            {% endif %}
            <div class="post-actions">
                <button class="action-btn comment" onclick="window.location.href='/posts/{{ p.id }}'">
                    <span class="action-icon">💬</span>
                    <span>Comment</span>
                </button>
                <button class="action-btn">
                    <span class="action-icon">🔄</span>
                    <span>Repost</span>
                </button>
                <button class="action-btn">
                    <span class="action-icon">❤️</span>
                    <span>{{ p.likes }}</span>
                </button>
                <button class="action-btn">
                    <span class="action-icon">📤</span>
                    <span>Share</span>
                </button>
            </div>
        </div>
        {% endfor %}
        
        {% if not posts %}
        <div style="padding: 40px 20px; text-align: center; color: var(--text-muted);">
            <p style="font-size: 20px; margin-bottom: 8px;">No posts yet</p>
            <p>Be the first to post something!</p>
        </div>
        {% endif %}
        """
        full_html = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', page_content)
        return render_template_string(full_html, posts=[dict(p) for p in posts])
    
    elif request.method == 'POST':
        if 'user_id' not in session:
            return redirect('/login')
            
        data = request.form if request.form else request.json
        user_id = session.get('user_id', 1)
        content = data.get('content', '')
        
        if not content.strip():
            return redirect('/posts')
        
        conn = get_db()
        # VULN: Stored XSS - no sanitization
        conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
        conn.commit()
        conn.close()
        
        return redirect('/posts')

@app.route('/posts/<post_id>', methods=['GET'])
def post_detail(post_id):
    """Post detail page with comments - VULN: IDOR"""
    conn = get_db()
    
    post = conn.execute('''SELECT p.*, u.username, u.avatar, u.id as user_id 
                          FROM posts p JOIN users u ON p.user_id = u.id 
                          WHERE p.id = ?''', (post_id,)).fetchone()
    
    if not post:
        conn.close()
        return "Post not found", 404
    
    comments_list = conn.execute('''SELECT c.*, u.username, u.avatar, u.id as user_id 
                                   FROM comments c JOIN users u ON c.user_id = u.id 
                                   WHERE c.post_id = ? ORDER BY c.created_at DESC''', (post_id,)).fetchall()
    
    conn.close()
    
    page_content = """
    <div style="border-bottom: 1px solid var(--border); padding: 16px 20px;">
        <a href="/posts" style="color: var(--primary); text-decoration: none; display: inline-flex; align-items: center; gap: 8px;">
            ← Back
        </a>
    </div>
    
    <div class="post-card">
        <div class="post-header">
            <a href="/profile/{{ p.user_id }}" class="avatar" style="text-decoration: none;">
                {{ p.username[0].upper() }}
            </a>
            <div class="post-info">
                <a href="/profile/{{ p.user_id }}" class="post-author">
                    {{ p.username }}
                    <span class="post-handle">@{{ p.username.lower() }}</span>
                </a>
                <div class="post-time">{{ p.created_at }}</div>
            </div>
        </div>
        <div class="post-content">
            {{ p.content | safe }}
        </div>
        {% if p.image_url %}
        <img src="/static/{{ p.image_url }}" class="post-image" alt="Post image">
        {% endif %}
        <div class="post-actions">
            <button class="action-btn comment">
                <span class="action-icon">💬</span>
                <span>{{ comments|length }}</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">🔄</span>
                <span>Repost</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">❤️</span>
                <span>{{ p.likes }}</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">📤</span>
                <span>Share</span>
            </button>
        </div>
    </div>
    
    {% if session.user_id %}
    <div class="post-composer">
        <form method="POST" action="/api/posts/{{ p.id }}/comments" style="display: flex; flex-direction: column;">
            <textarea name="content" class="composer-input" placeholder="Post your reply" rows="3" required></textarea>
            <div class="composer-actions">
                <div class="composer-icons"></div>
                <button type="submit" class="btn btn-sm">Reply</button>
            </div>
        </form>
    </div>
    {% else %}
    <div style="padding: 20px; text-align: center; border-bottom: 1px solid var(--border);">
        <p style="color: var(--text-muted); margin-bottom: 12px;">Want to comment?</p>
        <a href="/login" class="btn btn-sm" style="text-decoration: none; display: inline-block;">Login</a>
    </div>
    {% endif %}
    
    <div style="padding: 16px 20px; color: var(--text-muted); font-size: 15px; font-weight: 600; border-bottom: 1px solid var(--border);">
        Replies ({{ comments|length }})
    </div>
    
    {% for comment in comments %}
    <div class="post-card" style="padding-left: 60px;">
        <div class="post-header">
            <a href="/profile/{{ comment.user_id }}" class="avatar" style="text-decoration: none; width: 40px; height: 40px;">
                {{ comment.username[0].upper() }}
            </a>
            <div class="post-info">
                <a href="/profile/{{ comment.user_id }}" class="post-author">
                    {{ comment.username }}
                    <span class="post-handle">@{{ comment.username.lower() }}</span>
                </a>
                <div class="post-time">{{ comment.created_at }}</div>
            </div>
        </div>
        <div class="post-content">
            {{ comment.content | safe }}
        </div>
        <div class="post-actions">
            <button class="action-btn">
                <span class="action-icon">❤️</span>
            </button>
            <button class="action-btn">
                <span class="action-icon">💬</span>
            </button>
        </div>
    </div>
    {% endfor %}
    
    {% if not comments %}
    <div style="padding: 40px 20px; text-align: center; color: var(--text-muted);">
        <p>No replies yet. Be the first to reply!</p>
    </div>
    {% endif %}
    """
    
    full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Post').replace('{% block content %}{% endblock %}', page_content)
    return render_template_string(full_html, p=dict(post), comments=[dict(c) for c in comments_list])

@app.route('/api/posts/<post_id>', methods=['GET', 'DELETE'])
def post_detail_api(post_id):
    """Post detail API - VULN: IDOR in delete"""
    conn = get_db()
    
    if request.method == 'GET':
        post = conn.execute(f"SELECT * FROM posts WHERE id = {post_id}").fetchone()
        conn.close()
        return jsonify(dict(post)) if post else ('', 404)
    
    elif request.method == 'DELETE':
        # VULN: No authorization - can delete any post
        conn.execute(f"DELETE FROM posts WHERE id = {post_id}")
        conn.commit()
        conn.close()
        return jsonify({'message': 'Post deleted', 'vuln': 'IDOR'})

# ============================================================================
# COMMENTS
# ============================================================================

@app.route('/api/posts/<post_id>/comments', methods=['GET', 'POST'])
def comments(post_id):
    """Comments - VULN: Reflected XSS, Stored XSS"""
    conn = get_db()
    
    if request.method == 'GET':
        # VULN: Reflected XSS in search
        search = request.args.get('search', '')
        comments_list = conn.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,)).fetchall()
        conn.close()
        
        if request.is_json:
            return jsonify({
                'comments': [dict(c) for c in comments_list],
                'search': search,  # VULN: Reflected without sanitization
                'vuln': 'Reflected XSS' if search else None
            })
        else:
            return redirect(f'/posts/{post_id}')
    
    elif request.method == 'POST':
        data = request.json if request.json else request.form
        user_id = session.get('user_id', 1)
        content = data.get('content', '')
        
        if not content:
            conn.close()
            return redirect(f'/posts/{post_id}')
        
        # VULN: Stored XSS
        conn.execute('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
                    (post_id, user_id, content))
        conn.commit()
        conn.close()
        
        if request.is_json:
            return jsonify({'message': 'Comment added', 'vuln': 'Stored XSS'}), 201
        else:
            return redirect(f'/posts/{post_id}')

# ============================================================================
# FILE UPLOADS
# ============================================================================

def allowed_file(filename):
    # VULN: Weak validation
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload - VULN: Unrestricted file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No filename'}), 400
    
    # VULN: Can bypass with double extension (e.g., shell.php.jpg)
    # VULN: No file content validation
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({
        'message': 'File uploaded',
        'filename': filename,
        'url': f'/uploads/{filename}',
        'vuln': 'Unrestricted File Upload'
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files - VULN: Path traversal"""
    # VULN: No path validation - path traversal possible
    return send_from_directory(UPLOAD_FOLDER, filename)

# ============================================================================
# MESSAGES
# ============================================================================

@app.route('/messages/<user_id>', methods=['GET'])
def get_messages(user_id):
    """Get messages page - VULN: IDOR"""
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db()
    
    # Get conversation partner
    partner = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not partner:
        conn.close()
        return "User not found", 404
    
    # VULN: Can read anyone's messages - no authorization check
    messages = conn.execute('''SELECT m.*, 
                              u1.username as from_username, 
                              u2.username as to_username
                              FROM messages m
                              JOIN users u1 ON m.from_user_id = u1.id
                              JOIN users u2 ON m.to_user_id = u2.id
                              WHERE (m.to_user_id = ? AND m.from_user_id = ?) 
                              OR (m.to_user_id = ? AND m.from_user_id = ?)
                              ORDER BY m.created_at ASC''',
                           (user_id, session['user_id'], session['user_id'], user_id)).fetchall()
    
    conn.close()
    
    page_content = """
    <div style="max-width: 700px; margin: 0 auto;">
        <a href="/posts" style="color: var(--primary); text-decoration: none; margin-bottom: 1rem; display: inline-block;">
            ← Back to Feed
        </a>
        
        <div class="card" style="margin-top: 1rem;">
            <h2 style="margin-bottom: 1rem;">Messages with {{ partner.username }}</h2>
            
            <div style="max-height: 500px; overflow-y: auto; border: 1px solid var(--border); border-radius: 8px; padding: 1rem; background: #18191A; margin-bottom: 1rem;">
                {% for msg in messages %}
                <div style="margin-bottom: 1rem; {% if msg.from_user_id == session.user_id %}text-align: right;{% endif %}">
                    <div style="display: inline-block; background: {% if msg.from_user_id == session.user_id %}var(--primary){% else %}var(--card-bg){% endif %}; 
                                padding: 0.75rem 1rem; border-radius: 12px; max-width: 70%;">
                        <div style="font-size: 0.85rem; color: {% if msg.from_user_id == session.user_id %}#000{% else %}var(--text-main){% endif %}; 
                                    margin-bottom: 0.3rem; font-weight: 600;">{{ msg.from_username }}</div>
                        <div style="color: {% if msg.from_user_id == session.user_id %}#000{% else %}var(--text-main){% endif %};">{{ msg.content | safe }}</div>
                        <div style="font-size: 0.75rem; color: {% if msg.from_user_id == session.user_id %}rgba(0,0,0,0.6){% else %}var(--text-muted){% endif %}; 
                                    margin-top: 0.3rem;">{{ msg.created_at }}</div>
                    </div>
                </div>
                {% endfor %}
                
                {% if not messages %}
                <p style="text-align: center; color: var(--text-muted); padding: 2rem;">No messages yet. Start the conversation!</p>
                {% endif %}
            </div>
            
            <form method="POST" action="/api/messages/send">
                <input type="hidden" name="to_user_id" value="{{ partner.id }}">
                <textarea name="content" class="form-control" placeholder="Type a message..." rows="3" required></textarea>
                <button type="submit" class="btn" style="width: auto; margin-top: 0.5rem;">Send Message</button>
            </form>
        </div>
    </div>
    """
    
    full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Messages').replace('{% block content %}{% endblock %}', page_content)
    return render_template_string(full_html, messages=[dict(m) for m in messages], 
                                 partner=dict(partner), session=session)

@app.route('/api/messages/<user_id>', methods=['GET'])
def get_messages_api(user_id):
    """Get messages API - VULN: IDOR"""
    conn = get_db()
    # VULN: Can read anyone's messages
    messages = conn.execute('SELECT * FROM messages WHERE to_user_id = ? OR from_user_id = ?',
                           (user_id, user_id)).fetchall()
    conn.close()
    return jsonify({'messages': [dict(m) for m in messages], 'vuln': 'IDOR'})

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send message - VULN: Stored XSS"""
    data = request.json if request.json else request.form
    from_user_id = session.get('user_id', 1)
    to_user_id = data.get('to_user_id')
    content = data.get('content', '')
    
    if not content or not to_user_id:
        if request.is_json:
            return jsonify({'error': 'Missing content or recipient'}), 400
        else:
            return redirect(f'/messages/{to_user_id}')
    
    conn = get_db()
    # VULN: No XSS protection
    conn.execute('INSERT INTO messages (from_user_id, to_user_id, content) VALUES (?, ?, ?)',
                (from_user_id, to_user_id, content))
    conn.commit()
    conn.close()
    
    if request.is_json:
        return jsonify({'message': 'Message sent', 'vuln': 'Stored XSS'}), 201
    else:
        return redirect(f'/messages/{to_user_id}')

# ============================================================================
# FRIENDSHIPS
# ============================================================================

@app.route('/api/friends/add', methods=['POST'])
def add_friend():
    """Add friend - VULN: CSRF"""
    data = request.json
    user_id = session.get('user_id', 1)
    friend_id = data.get('friend_id')
    
    # VULN: No CSRF protection
    conn = get_db()
    conn.execute('INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, ?)',
                (user_id, friend_id, 'accepted'))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Friend added', 'vuln': 'CSRF'})

# ============================================================================
# SEARCH
# ============================================================================

@app.route('/search', methods=['GET'])
def search():
    """Search - VULN: SQL Injection"""
    query = request.args.get('q', '')
    
    if not query:
        page_content = """
        <div style="max-width: 600px; margin: 0 auto; margin-top: 3rem;">
            <h1 style="margin-bottom: 2rem;">Search Users</h1>
            <form action="/search" method="GET" style="display: flex; gap: 1rem;">
                <input type="text" name="q" class="form-control" placeholder="Search by username or bio..." 
                       value="" style="flex: 1;">
                <button type="submit" class="btn" style="width: auto;">Search</button>
            </form>
        </div>
        """
        full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Explore').replace('{% block content %}{% endblock %}', page_content)
        return render_template_string(full_html)
    
    conn = get_db()
    # VULN: SQL Injection
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR bio LIKE '%{query}%'"
    
    try:
        results = conn.execute(sql).fetchall()
        conn.close()
        
        page_content = """
        <div style="max-width: 700px; margin: 0 auto;">
            <a href="/posts" style="color: var(--primary); text-decoration: none; margin-bottom: 1rem; display: inline-block;">
                ← Back to Feed
            </a>
            
            <h1 style="margin-bottom: 1rem;">Search Results for "{{ q }}"</h1>
            
            <form action="/search" method="GET" style="display: flex; gap: 1rem; margin-bottom: 2rem;">
                <input type="text" name="q" class="form-control" placeholder="Search by username or bio..." 
                       value="{{ q }}" style="flex: 1;">
                <button type="submit" class="btn" style="width: auto;">Search</button>
            </form>
            
            {% if results %}
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                {% for u in results %}
                <div class="card">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div class="avatar" style="width: 60px; height: 60px;"></div>
                        <div style="flex: 1;">
                            <h2 style="margin-bottom: 0.3rem;">
                                <a href="/profile/{{ u.id }}" style="color: white; text-decoration: none;">{{ u.username }}</a>
                            </h2>
                            <p style="color: var(--text-muted); margin: 0;">{{ u.bio }}</p>
                        </div>
                        <div>
                            <a href="/profile/{{ u.id }}" class="btn btn-outline" style="width: auto; text-decoration: none;">View Profile</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="card" style="text-align: center; padding: 3rem;">
                <p style="color: var(--text-muted); font-size: 1.1rem;">No users found for "{{ q }}"</p>
                <p style="color: var(--text-muted); margin-top: 0.5rem;">Try a different search term</p>
            </div>
            {% endif %}
        </div>
        """
        full_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Search').replace('{% block content %}{% endblock %}', page_content)
        return render_template_string(full_html, results=[dict(u) for u in results], q=query)

    except Exception as e:
        conn.close()
        error_content = f"""
        <div class="alert">
            <strong>Database Error:</strong> {str(e)}
            <br><small>This might indicate a SQL injection vulnerability!</small>
        </div>
        """
        error_html = HTML_TEMPLATE.replace('{% block header %}Home{% endblock %}', 'Search').replace('{% block content %}{% endblock %}', error_content)
        return render_template_string(error_html)

# ============================================================================
# MISC
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'app': 'Social Media Platform'})

@app.route('/')
def index():
    return redirect('/posts')

if __name__ == '__main__':
    print("=" * 70)
    print("VULNERABLE SOCIAL MEDIA - Research Variant 2")
    print("=" * 70)
    print("DELIBERATELY VULNERABLE - For Research & Training Only!")
    print("=" * 70)
    print("\nFocus Areas:")
    print("   - XSS (stored in posts/comments, reflected in search)")
    print("   - Authentication (weak passwords, session fixation, predictable tokens)")
    print("   - File uploads (unrestricted, path traversal)")
    print("   - IDOR (profiles, messages, posts)")
    print("   - CSRF (friend requests)")
    print("   - SQL injection in search")
    init_db()
    print("\n Starting on http://localhost:5003\n")
    print("=" * 70)
    app.run(port=5003, debug=True)