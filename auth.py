import requests
import sqlite3
import hashlib

API_URL = "http://localhost:8000"
DB_FILE = "fintrend.db"

def init_local_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    # Watchlist table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            username TEXT,
            ticker TEXT,
            PRIMARY KEY (username, ticker),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    # Portfolio table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ticker TEXT,
            shares REAL,
            buy_price REAL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    try:
        r = requests.post(f"{API_URL}/signup", json={"username": username, "password": password}, timeout=1.5)
        if r.status_code == 200:
            return True, r.json()["message"]
        return False, r.json().get("detail", "Error creating account")
    except Exception:
        # Fallback to local SQLite database directly (e.g. on Streamlit Cloud)
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Username already exists"
            
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                           (username, hash_password(password)))
            conn.commit()
            conn.close()
            return True, "Account created successfully (Local Mode)"
        except Exception as e:
            return False, f"Database error: {str(e)}"

def login(username, password):
    try:
        r = requests.post(f"{API_URL}/login", json={"username": username, "password": password}, timeout=1.5)
        if r.status_code == 200:
            return True, r.json()["message"]
        return False, r.json().get("detail", "Invalid credentials")
    except Exception:
        # Fallback to local SQLite database directly (e.g. on Streamlit Cloud)
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
            row = cursor.fetchone()
            conn.close()
            if not row or row[0] != hash_password(password):
                return False, "Invalid credentials"
            return True, "Login successful (Local Mode)"
        except Exception as e:
            return False, f"Database error: {str(e)}"

def get_watchlist(username):
    try:
        r = requests.get(f"{API_URL}/watchlist/{username}", timeout=1.5)
        if r.status_code == 200:
            return r.json().get("watchlist", [])
        return []
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT ticker FROM watchlist WHERE username=?", (username,))
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tickers
        except:
            return []

def add_to_watchlist(username, ticker):
    try:
        r = requests.post(f"{API_URL}/watchlist/add", json={"username": username, "ticker": ticker}, timeout=1.5)
        return r.status_code == 200
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO watchlist (username, ticker) VALUES (?, ?)", (username, ticker))
            conn.commit()
            conn.close()
            return True
        except:
            return False

def remove_from_watchlist(username, ticker):
    try:
        r = requests.post(f"{API_URL}/watchlist/remove", json={"username": username, "ticker": ticker}, timeout=1.5)
        return r.status_code == 200
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE username=? AND ticker=?", (username, ticker))
            conn.commit()
            conn.close()
            return True
        except:
            return False

def get_portfolio(username):
    try:
        r = requests.get(f"{API_URL}/portfolio/{username}", timeout=1.5)
        if r.status_code == 200:
            return r.json().get("portfolio", [])
        return []
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT ticker, shares, buy_price FROM portfolio WHERE username=?", (username,))
            trades = [{"ticker": row[0], "shares": row[1], "buy_price": row[2]} for row in cursor.fetchall()]
            conn.close()
            return trades
        except:
            return []

def buy_portfolio_item(username, ticker, shares, price):
    try:
        r = requests.post(f"{API_URL}/portfolio/buy", json={"username": username, "ticker": ticker, "shares": shares, "price": price}, timeout=1.5)
        return r.status_code == 200
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO portfolio (username, ticker, shares, buy_price) VALUES (?, ?, ?, ?)", 
                           (username, ticker, shares, price))
            conn.commit()
            conn.close()
            return True
        except:
            return False

def sell_portfolio_item(username, ticker, shares, price=0):
    try:
        r = requests.post(f"{API_URL}/portfolio/sell", json={"username": username, "ticker": ticker, "shares": shares, "price": price}, timeout=1.5)
        return r.status_code == 200
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, shares FROM portfolio WHERE username=? AND ticker=?", (username, ticker))
            holdings = cursor.fetchall()
            
            shares_to_sell = shares
            for h_id, h_shares in holdings:
                if shares_to_sell <= 0:
                    break
                if h_shares <= shares_to_sell:
                    cursor.execute("DELETE FROM portfolio WHERE id=?", (h_id,))
                    shares_to_sell -= h_shares
                else:
                    cursor.execute("UPDATE portfolio SET shares=? WHERE id=?", (h_shares - shares_to_sell, h_id))
                    shares_to_sell = 0
            conn.commit()
            conn.close()
            return True
        except:
            return False
