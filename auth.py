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
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ticker TEXT,
            trade_type TEXT,
            shares REAL,
            price REAL,
            brokerage REAL,
            stt REAL,
            exchange_charges REAL,
            sebi_fees REAL,
            gst REAL,
            stamp_duty REAL,
            dp_charges REAL,
            total_charges REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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

def calculate_charges(trade_type: str, shares: float, price: float) -> dict:
    value = shares * price
    # Brokerage: flat ₹20 or 0.03% (whichever is lower) for delivery
    brokerage = min(20.0, 0.0003 * value)
    # STT: 0.1% on buy & sell for delivery
    stt = 0.001 * value
    # Exchange Transaction Charges (NSE): 0.00322%
    exchange_charges = 0.0000322 * value
    # SEBI Turnover Fee: 0.0001% (₹10/crore)
    sebi_fees = 0.000001 * value
    # GST: 18% on (Brokerage + Exchange Charges + SEBI Fees)
    gst = 0.18 * (brokerage + exchange_charges + sebi_fees)
    # Stamp Duty: 0.015% on BUY only
    stamp_duty = 0.00015 * value if trade_type.upper() == 'BUY' else 0.0
    # DP Charges: ₹15.93 (13.5 + GST) on SELL only
    dp_charges = 15.93 if trade_type.upper() == 'SELL' else 0.0
    
    total = brokerage + stt + exchange_charges + sebi_fees + gst + stamp_duty + dp_charges
    
    return {
        "brokerage": brokerage,
        "stt": stt,
        "exchange_charges": exchange_charges,
        "sebi_fees": sebi_fees,
        "gst": gst,
        "stamp_duty": stamp_duty,
        "dp_charges": dp_charges,
        "total": total
    }

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
            
            # Log transaction fallback
            chg = calculate_charges("BUY", shares, price)
            cursor.execute('''
                INSERT INTO transactions 
                (username, ticker, trade_type, shares, price, brokerage, stt, exchange_charges, sebi_fees, gst, stamp_duty, dp_charges, total_charges)
                VALUES (?, ?, 'BUY', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, ticker, shares, price, 
                  chg["brokerage"], chg["stt"], chg["exchange_charges"], chg["sebi_fees"], 
                  chg["gst"], chg["stamp_duty"], chg["dp_charges"], chg["total"]))
                  
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
            
            total_held = sum(h[1] for h in holdings)
            if total_held < shares:
                conn.close()
                return False
                
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
                    
            # Log transaction fallback
            chg = calculate_charges("SELL", shares, price)
            cursor.execute('''
                INSERT INTO transactions 
                (username, ticker, trade_type, shares, price, brokerage, stt, exchange_charges, sebi_fees, gst, stamp_duty, dp_charges, total_charges)
                VALUES (?, ?, 'SELL', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, ticker, shares, price, 
                  chg["brokerage"], chg["stt"], chg["exchange_charges"], chg["sebi_fees"], 
                  chg["gst"], chg["stamp_duty"], chg["dp_charges"], chg["total"]))
                  
            conn.commit()
            conn.close()
            return True
        except:
            return False

def get_transactions(username):
    try:
        r = requests.get(f"{API_URL}/portfolio/transactions/{username}", timeout=1.5)
        if r.status_code == 200:
            return r.json().get("transactions", [])
        return []
    except Exception:
        try:
            init_local_db()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ticker, trade_type, shares, price, brokerage, stt, exchange_charges, sebi_fees, gst, stamp_duty, dp_charges, total_charges, timestamp
                FROM transactions WHERE username=? ORDER BY timestamp DESC
            ''', (username,))
            rows = cursor.fetchall()
            conn.close()
            
            txs = []
            for r in rows:
                txs.append({
                    "ticker": r[0],
                    "trade_type": r[1],
                    "shares": r[2],
                    "price": r[3],
                    "brokerage": r[4],
                    "stt": r[5],
                    "exchange_charges": r[6],
                    "sebi_fees": r[7],
                    "gst": r[8],
                    "stamp_duty": r[9],
                    "dp_charges": r[10],
                    "total_charges": r[11],
                    "timestamp": r[12]
                })
            return txs
        except:
            return []
