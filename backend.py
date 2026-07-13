from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib
import os

app = FastAPI(title="FinTrend Backend API")

VERCEL = os.environ.get("VERCEL") == "1"

if VERCEL:
    DB_FILE = "/tmp/fintrend.db"
else:
    DB_FILE = "fintrend.db"

def init_db():
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

init_db()

@app.get("/")
def read_root():
    return {"status": "online", "message": "FinTrend Backend API is running successfully"}

# --- Models ---
class User(BaseModel):
    username: str
    password: str

class WatchlistItem(BaseModel):
    username: str
    ticker: str

class PortfolioTrade(BaseModel):
    username: str
    ticker: str
    shares: float
    price: float

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Auth Routes ---
@app.post("/signup")
def signup(user: User):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username=?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                   (user.username, hash_password(user.password)))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: User):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (user.username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "username": user.username}

# --- Watchlist Routes ---
@app.get("/watchlist/{username}")
def get_watchlist(username: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM watchlist WHERE username=?", (username,))
    tickers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"watchlist": tickers}

@app.post("/watchlist/add")
def add_watchlist(item: WatchlistItem):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO watchlist (username, ticker) VALUES (?, ?)", (item.username, item.ticker))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already exists
    finally:
        conn.close()
    return {"message": f"{item.ticker} added to watchlist"}

@app.post("/watchlist/remove")
def remove_watchlist(item: WatchlistItem):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE username=? AND ticker=?", (item.username, item.ticker))
    conn.commit()
    conn.close()
    return {"message": f"{item.ticker} removed from watchlist"}

# --- Portfolio Routes ---
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

@app.get("/portfolio/{username}")
def get_portfolio(username: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, shares, buy_price FROM portfolio WHERE username=?", (username,))
    trades = [{"ticker": row[0], "shares": row[1], "buy_price": row[2]} for row in cursor.fetchall()]
    conn.close()
    return {"portfolio": trades}

@app.post("/portfolio/buy")
def buy_stock(trade: PortfolioTrade):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO portfolio (username, ticker, shares, buy_price) VALUES (?, ?, ?, ?)", 
                   (trade.username, trade.ticker, trade.shares, trade.price))
    
    # Calculate and log charges & transaction history
    chg = calculate_charges("BUY", trade.shares, trade.price)
    cursor.execute('''
        INSERT INTO transactions 
        (username, ticker, trade_type, shares, price, brokerage, stt, exchange_charges, sebi_fees, gst, stamp_duty, dp_charges, total_charges)
        VALUES (?, ?, 'BUY', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trade.username, trade.ticker, trade.shares, trade.price, 
          chg["brokerage"], chg["stt"], chg["exchange_charges"], chg["sebi_fees"], 
          chg["gst"], chg["stamp_duty"], chg["dp_charges"], chg["total"]))
          
    conn.commit()
    conn.close()
    return {"message": f"Bought {trade.shares} of {trade.ticker}"}

@app.post("/portfolio/sell")
def sell_stock(trade: PortfolioTrade):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Find holdings of this ticker to verify we have enough shares
    cursor.execute("SELECT id, shares FROM portfolio WHERE username=? AND ticker=?", (trade.username, trade.ticker))
    holdings = cursor.fetchall()
    
    total_held = sum(h[1] for h in holdings)
    if total_held < trade.shares:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Insufficient holdings. You only hold {total_held} shares.")
        
    shares_to_sell = trade.shares
    for h_id, h_shares in holdings:
        if shares_to_sell <= 0:
            break
        if h_shares <= shares_to_sell:
            # Sell entire lot
            cursor.execute("DELETE FROM portfolio WHERE id=?", (h_id,))
            shares_to_sell -= h_shares
        else:
            # Sell partial lot
            cursor.execute("UPDATE portfolio SET shares=? WHERE id=?", (h_shares - shares_to_sell, h_id))
            shares_to_sell = 0
            
    # Calculate and log charges & transaction history
    chg = calculate_charges("SELL", trade.shares, trade.price)
    cursor.execute('''
        INSERT INTO transactions 
        (username, ticker, trade_type, shares, price, brokerage, stt, exchange_charges, sebi_fees, gst, stamp_duty, dp_charges, total_charges)
        VALUES (?, ?, 'SELL', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trade.username, trade.ticker, trade.shares, trade.price, 
          chg["brokerage"], chg["stt"], chg["exchange_charges"], chg["sebi_fees"], 
          chg["gst"], chg["stamp_duty"], chg["dp_charges"], chg["total"]))
          
    conn.commit()
    conn.close()
    return {"message": f"Sold {trade.shares} of {trade.ticker}"}

@app.get("/portfolio/transactions/{username}")
def get_transactions(username: str):
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
    return {"transactions": txs}
