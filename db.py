import sqlite3
import hashlib

def hash256(content: str):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def init():
    db = get_db()
    cursor = db.cursor()
    cursor.executescript(open("db/schema.sql").read())

def get_user_id(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    db.close()

    return result[0] if result else None

def get_user_by_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (id,))
    result = cursor.fetchone()

    db.close()

    return result[0] if result else None

def add_ip_for_user(ip_address, user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM addresses WHERE ip = ? AND user_id = ?", (ip_address, user_id))
    result = cursor.fetchone()

    if result:
        print(f"IP {ip_address} is already associated with user ID {user_id}.")
    else:
        cursor.execute("INSERT INTO addresses (ip, user_id) VALUES (?, ?)", (ip_address, user_id))
        db.commit()
        print(f"IP {ip_address} added for user ID {user_id}.")

    db.close()


def get_user_by_ip(ip_address):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT user_id FROM addresses WHERE ip = ?", (ip_address,))
    result = cursor.fetchone()
    db.close()

    if result and result[0] is not None:
        return result[0]
    else:
        return False

def get_db():
    return sqlite3.connect('db/database.db')

def check_user(username):
    cursor = get_db().cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result is not None

def check_password(username,password):
    cursor = get_db().cursor()
    password = hash256(password)
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    return result is not None and result[0] == password

def create_user(username,password):
    db = get_db()
    cursor = db.cursor()
    hashed_password = hash256(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        db.commit()
        return f"User {username} created succesfully"
    except sqlite3.IntegrityError:
        return "Error: Username already exists."
