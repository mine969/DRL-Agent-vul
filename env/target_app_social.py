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
    <title>SocialNet</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2D88FF;
            --bg: #18191A;
            --card-bg: #242526;
            --text-main: #E4E6EB;
            --text-muted: #B0B3B8;
            --border: #3E4042;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
        }
        .navbar {
            background: var(--card-bg);
            padding: 0 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 60px;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
        }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 500;
            padding: 8px 12px;
            border-radius: 8px;
        }
        .nav-links a:hover, .nav-links a.active {
            background: rgba(45, 136, 255, 0.1);
            color: var(--primary);
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 0 1rem;
        }
        
        /* Cards & Feed */
        .card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        .post-header { display: flex; gap: 10px; margin-bottom: 10px; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #555; }
        .post-content { font-size: 1.1rem; margin-bottom: 1rem; }
        .post-actions {
            border-top: 1px solid var(--border);
            padding-top: 0.5rem;
            display: flex;
            gap: 1rem;
        }
        
        /* Forms */
        .form-control {
            width: 100%;
            padding: 10px;
            background: #3A3B3C;
            border: 1px solid var(--border);
            border-radius: 20px;
            color: var(--text-main);
            margin-bottom: 10px;
            box-sizing: border-box;
        }
        .btn {
            background: var(--primary);
            color: white;
            padding: 8px 30px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        .btn-outline {
            background: transparent;
            border: 1px solid var(--primary);
            color: var(--primary);
        }
        
        .alert {
            padding: 1rem;
            background: rgba(255, 76, 76, 0.2);
            color: #ff4c4c;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">SocialNet</a>
        <div class="nav-links">
            <a href="/">Feed</a>
            {% if session.user_id %}
                <a href="/profile/{{ session.user_id }}">My Profile</a>
                <a href="/messages/{{ session.user_id }}">Messages</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/register">Join</a>
            {% endif %}
        </div>
    </nav>
    
    <div class="container">
        {% if error %}<div class="alert">{{ error }}</div>{% endif %}
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
        return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', page_content))

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
        return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', f'<div class="alert">Error: {str(e)}</div>'))
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
        full_html = HTML_TEMPLATE.replace('{{ content | safe }}', page_content)
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
    
    return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', '<div class="alert">Invalid Credentials</div>'))

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
    user = conn.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    conn.close()
    
    if user:
        page_content = """
        <div class="card" style="margin-top: 2rem;">
            <div style="background: linear-gradient(90deg, var(--primary), #888); height: 150px; border-radius: 8px 8px 0 0;"></div>
            <div style="padding: 2rem; position: relative;">
                <div style="width: 120px; height: 120px; border-radius: 50%; background: #333; border: 4px solid var(--card-bg); position: absolute; top: -60px;"></div>
                <div style="margin-top: 40px;">
                    <h1>{{ u.username }}</h1>
                    <p style="color: #ccc;">{{ u.bio }}</p>
                    <div style="margin-top: 1rem;">
                        <button class="btn" style="width: auto;">Follow</button>
                        <button class="btn btn-outline" style="width: auto;">Message</button>
                    </div>
                </div>
            </div>
        </div>
        """
        full_html = HTML_TEMPLATE.replace('{{ content | safe }}', page_content)
        return render_template_string(full_html, u=user)
    
    return "User not found", 404

# ============================================================================
# POSTS
# ============================================================================

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    """Posts - VULN: Stored XSS"""
    conn = get_db()
    
    if request.method == 'GET':
        posts = conn.execute('SELECT p.*, u.username, u.avatar FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC').fetchall()
        conn.close()
        
        page_content = """
        <div class="row">
            <div class="col" style="max-width: 600px; margin: 0 auto;">
                {% if session.user_id %}
                <div class="card">
                    <form action="/posts" method="POST">
                        <textarea name="content" class="form-control" placeholder="What's on your mind?" rows="3"></textarea>
                        <div style="text-align: right;">
                            <button type="submit" class="btn" style="width: auto;">Post</button>
                        </div>
                    </form>
                </div>
                {% endif %}
                
                {% for p in posts %}
                <div class="card">
                    <div class="post-header">
                        <div class="avatar"></div> <!-- Placeholder for avatar img -->
                        <div>
                            <div style="font-weight: bold;">{{ p.username }}</div>
                            <div style="font-size: 0.8rem; color: #B0B3B8;">{{ p.created_at }}</div>
                        </div>
                    </div>
                    <div class="post-content">
                        {{ p.content | safe }} <!-- VULN: XSS is rendered here -->
                    </div>
                    {% if p.image_url %}
                    <img src="/static/{{ p.image_url }}" style="width: 100%; border-radius: 8px; margin-top: 10px;">
                    {% endif %}
                    <div class="post-actions">
                        <button class="btn btn-outline" style="width: auto;">Like ({{ p.likes }})</button>
                        <a href="/posts/{{ p.id }}" class="btn btn-outline" style="width: auto; text-decoration: none;">Comment</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        """
        full_html = HTML_TEMPLATE.replace('{{ content | safe }}', page_content)
        return render_template_string(full_html, posts=posts)
    
    elif request.method == 'POST':
        data = request.form if request.form else request.json
        user_id = session.get('user_id', 1)
        content = data.get('content', '')
        
        # VULN: Stored XSS - no sanitization
        conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
        conn.commit()
        conn.close()
        
        return redirect('/posts')

@app.route('/posts/<post_id>', methods=['GET'])
def post_detail(post_id):
    """Post detail page with comments - VULN: IDOR"""
    conn = get_db()
    
    post = conn.execute('''SELECT p.*, u.username, u.avatar 
                          FROM posts p JOIN users u ON p.user_id = u.id 
                          WHERE p.id = ?''', (post_id,)).fetchone()
    
    if not post:
        conn.close()
        return "Post not found", 404
    
    comments_list = conn.execute('''SELECT c.*, u.username, u.avatar 
                                   FROM comments c JOIN users u ON c.user_id = u.id 
                                   WHERE c.post_id = ? ORDER BY c.created_at DESC''', (post_id,)).fetchall()
    
    conn.close()
    
    page_content = """
    <div style="max-width: 700px; margin: 0 auto;">
        <a href="/posts" style="color: var(--primary); text-decoration: none; margin-bottom: 1rem; display: inline-block;">
            ← Back to Feed
        </a>
        
        <div class="card" style="margin-top: 1rem;">
            <div class="post-header">
                <div class="avatar"></div>
                <div>
                    <div style="font-weight: bold;">
                        <a href="/profile/{{ p.user_id }}" style="color: white; text-decoration: none;">{{ p.username }}</a>
                    </div>
                    <div style="font-size: 0.8rem; color: #B0B3B8;">{{ p.created_at }}</div>
                </div>
            </div>
            <div class="post-content">
                {{ p.content | safe }}
            </div>
            {% if p.image_url %}
            <img src="/static/{{ p.image_url }}" style="width: 100%; border-radius: 8px; margin-top: 10px;">
            {% endif %}
            <div class="post-actions">
                <button class="btn btn-outline" style="width: auto;">Like ({{ p.likes }})</button>
            </div>
        </div>
        
        <div class="card" style="margin-top: 1rem;">
            <h3 style="margin-bottom: 1rem;">Comments ({{ comments|length }})</h3>
            
            {% if session.user_id %}
            <form method="POST" action="/api/posts/{{ p.id }}/comments" style="margin-bottom: 2rem;">
                <textarea name="content" class="form-control" placeholder="Write a comment..." rows="3" required></textarea>
                <button type="submit" class="btn" style="width: auto; margin-top: 0.5rem;">Post Comment</button>
            </form>
            {% else %}
            <p style="color: var(--text-muted); margin-bottom: 1rem;">
                <a href="/login" style="color: var(--primary);">Login</a> to comment
            </p>
            {% endif %}
            
            {% for comment in comments %}
            <div style="padding: 1rem 0; border-bottom: 1px solid var(--border);">
                <div style="display: flex; gap: 10px;">
                    <div class="avatar" style="width: 32px; height: 32px;"></div>
                    <div style="flex: 1;">
                        <div style="font-weight: bold; margin-bottom: 0.3rem;">
                            <a href="/profile/{{ comment.user_id }}" style="color: white; text-decoration: none;">{{ comment.username }}</a>
                        </div>
                        <div style="color: var(--text-main); margin-bottom: 0.5rem;">{{ comment.content | safe }}</div>
                        <div style="font-size: 0.8rem; color: #B0B3B8;">{{ comment.created_at }}</div>
                    </div>
                </div>
            </div>
            {% endfor %}
            
            {% if not comments %}
            <p style="text-align: center; color: var(--text-muted); padding: 2rem;">No comments yet. Be the first to comment!</p>
            {% endif %}
        </div>
    </div>
    """
    
    full_html = HTML_TEMPLATE.replace('{{ content | safe }}', page_content)
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

@app.route('/api/messages/<user_id>', methods=['GET'])
def get_messages(user_id):
    """Get messages - VULN: IDOR"""
    conn = get_db()
    # VULN: Can read anyone's messages
    messages = conn.execute('SELECT * FROM messages WHERE to_user_id = ? OR from_user_id = ?',
                           (user_id, user_id)).fetchall()
    conn.close()
    return jsonify({'messages': [dict(m) for m in messages], 'vuln': 'IDOR'})

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send message - VULN: Stored XSS"""
    data = request.json
    from_user_id = session.get('user_id', 1)
    to_user_id = data.get('to_user_id')
    content = data.get('content', '')
    
    conn = get_db()
    # VULN: No XSS protection
    conn.execute('INSERT INTO messages (from_user_id, to_user_id, content) VALUES (?, ?, ?)',
                (from_user_id, to_user_id, content))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Message sent', 'vuln': 'Stored XSS'}), 201

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
    
    conn = get_db()
    # VULN: SQL Injection
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR bio LIKE '%{query}%'"
    
    try:
        results = conn.execute(sql).fetchall()
        conn.close()
        
        page_content = """
        <div style="margin-bottom: 2rem;">
            <h1>Search Results for "{{ q }}"</h1>
        </div>
        
        {% for u in results %}
        <div class="card">
            <div style="display: flex; align-items: center;">
                <div class="avatar" style="width: 60px; height: 60px;"></div>
                <div>
                    <h2><a href="/profile/{{ u.id }}" style="color: white; text-decoration: none;">{{ u.username }}</a></h2>
                    <p>{{ u.bio }}</p>
                </div>
            </div>
        </div>
        {% endfor %}
        
        {% if not results %}
        <p>No users found.</p>
        {% endif %}
        """
        full_html = HTML_TEMPLATE.replace('{{ content | safe }}', page_content)
        return render_template_string(full_html, results=results, q=query)

    except Exception as e:
        conn.close()
        return render_template_string(HTML_TEMPLATE.replace('{{ content | safe }}', f'<div class="alert">Database Error: {str(e)}</div>'))

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
