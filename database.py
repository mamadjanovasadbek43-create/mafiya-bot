import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "mafiya.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                diamonds INTEGER DEFAULT 20,
                coins INTEGER DEFAULT 100,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                item_name TEXT,
                used INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user INTEGER,
                to_user INTEGER,
                amount INTEGER,
                currency TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def add_user(self, user_id, name, username):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        self.conn.commit()

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_reward(self, user_id, diamonds=0, coins=0):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET diamonds = diamonds + ?, coins = coins + ?, games_played = games_played + 1 WHERE user_id = ?", (diamonds, coins, user_id))
        self.conn.commit()

    def transfer_coins(self, from_id, to_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (amount, from_id))
        cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, to_id))
        cursor.execute("INSERT INTO transactions (from_user, to_user, amount, currency) VALUES (?, ?, ?, 'coins')", (from_id, to_id, amount))
        self.conn.commit()

    def buy_item(self, user_id, item_id, currency, price):
        cursor = self.conn.cursor()
        if currency == 'diamonds':
            cursor.execute("UPDATE users SET diamonds = diamonds - ? WHERE user_id = ?", (price, user_id))
        else:
            cursor.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (price, user_id))
        self.conn.commit()

    def add_inventory(self, user_id, item_id, item_name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO inventory (user_id, item_id, item_name) VALUES (?, ?, ?)", (user_id, item_id, item_name))
        self.conn.commit()

    def get_inventory(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE user_id = ? AND used = 0", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
