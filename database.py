import sqlite3
import hashlib
import os

DB_FILE = "users.db"

# ==========================================
# PASSWORD CRYPTOGRAPHY HELPERS
# ==========================================

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    try:
        salt_hex, key_hex = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return key == new_key
    except Exception:
        return False


# ==========================================
# DATABASE INITIALIZATION & BASE ACTIONS
# ==========================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Users Table (Added approved column)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            isadmin INTEGER DEFAULT 0,
            isenable INTEGER DEFAULT 1,
            approved INTEGER DEFAULT 0
        )
    ''')
    
    # 2. Game Records Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            game_name TEXT,
            playtime TEXT,
            levels TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # 3. Games Selection Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    
    # Pre-populate default accounts (Both ryan and xindong are pre-approved = 1)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        hashed_ryan = hash_password("12345")
        hashed_xindong = hash_password("00000")
        
        cursor.execute("INSERT INTO users (username, password, isadmin, isenable, approved) VALUES (?, ?, 0, 1, 1)", ("ryan", hashed_ryan))
        cursor.execute("INSERT INTO users (username, password, isadmin, isenable, approved) VALUES (?, ?, 1, 1, 1)", ("xindong", hashed_xindong))
        conn.commit()

    # Pre-populate default games list
    cursor.execute("SELECT COUNT(*) FROM games")
    if cursor.fetchone()[0] == 0:
        default_games = [
            "Minecraft", 
            "Elden Ring", 
            "Valorant", 
            "League of Legends", 
            "Grand Theft Auto V", 
            "Cyberpunk 2077", 
            "Hades"
        ]
        cursor.executemany("INSERT INTO games (name) VALUES (?)", [(g,) for g in default_games])
        conn.commit()

    conn.close()

def get_user_profile(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password, isadmin, isenable, approved FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "password": result[0],
            "isadmin": bool(result[1]),
            "isenable": bool(result[2]),
            "approved": bool(result[3])
        }
    return None

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        
        # New users default to approved = 0 and isenable = 0
        cursor.execute("INSERT INTO users (username, password, isadmin, isenable, approved) VALUES (?, ?, 0, 0, 0)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_games():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM games ORDER BY name ASC")
    games = [row[0] for row in cursor.fetchall()]
    conn.close()
    return games


# ==========================================
# ADMIN FUNCTIONS
# ==========================================

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, isadmin, isenable, approved FROM users")
    users = cursor.fetchall()
    conn.close()
    return [
        {
            "username": row[0], 
            "isadmin": bool(row[1]), 
            "isenable": bool(row[2]), 
            "approved": bool(row[3])
        } 
        for row in users
    ]

def approve_user(username):
    """Sets approved to 1 and enables the user so they can log in."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET approved = 1, isenable = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def set_user_status(username, isenable):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET isenable = ? WHERE username = ?", (isenable, username))
    conn.commit()
    conn.close()

def set_admin_status(username, isadmin):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET isadmin = ? WHERE username = ?", (isadmin, username))
    conn.commit()
    conn.close()


# ==========================================
# GAME RECORD FUNCTIONS
# ==========================================

def get_game_records(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, game_name, playtime, levels FROM game_records WHERE username = ?", (username,))
    records = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "game_name": row[1], "playtime": row[2], "levels": row[3]} for row in records]

def get_single_record(record_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, game_name, playtime, levels FROM game_records WHERE id = ? AND username = ?", (record_id, username))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "game_name": row[1], "playtime": row[2], "levels": row[3]}
    return None

def add_game_record(username, game_name, playtime, levels):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO game_records (username, game_name, playtime, levels) VALUES (?, ?, ?, ?)", (username, game_name, playtime, levels))
    conn.commit()
    conn.close()

def update_game_record(record_id, username, game_name, playtime, levels):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE game_records 
        SET game_name = ?, playtime = ?, levels = ? 
        WHERE id = ? AND username = ?
    ''', (game_name, playtime, levels, record_id, username))
    conn.commit()
    conn.close()

def delete_game_record(record_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM game_records WHERE id = ? AND username = ?", (record_id, username))
    conn.commit()
    conn.close()