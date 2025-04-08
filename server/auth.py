import sqlite3
import bcrypt

DB_PATH = "../db/email_server.db"

def signup(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hash the password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        print(f"[✓] User '{username}' signed up.")
        return True
    except sqlite3.IntegrityError:
        print(f"[!] Username '{username}' already exists.")
        return False
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0]):
        print(f"[✓] Login successful for '{username}'")
        return True
    else:
        print(f"[!] Login failed for '{username}'")
        return False

