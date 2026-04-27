from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib
import os

app = FastAPI(title="FinTrend Backend API")

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
    conn.commit()
    conn.close()

init_db()

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
    conn.commit()
    conn.close()
    return {"message": f"Bought {trade.shares} of {trade.ticker}"}

@app.post("/portfolio/sell")
def sell_stock(trade: PortfolioTrade):
    # For simplicity, we just delete the specific holding, or we can deduct shares.
    # In a real app, we'd calculate average price or matching lots.
    # Here, we will just delete the first matching lot or enough lots.
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Find holdings of this ticker
    cursor.execute("SELECT id, shares FROM portfolio WHERE username=? AND ticker=?", (trade.username, trade.ticker))
    holdings = cursor.fetchall()
    
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
            
    conn.commit()
    conn.close()
    
    if shares_to_sell > 0:
         return {"message": "Sold partial shares, did not have enough holding"}
    return {"message": f"Sold {trade.shares} of {trade.ticker}"}
