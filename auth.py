import requests

API_URL = "http://localhost:8000"

def signup(username, password):
    try:
        r = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
        if r.status_code == 200:
            return True, r.json()["message"]
        return False, r.json().get("detail", "Error creating account")
    except Exception as e:
        return False, f"Backend connection error: {e}"

def login(username, password):
    try:
        r = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if r.status_code == 200:
            return True, r.json()["message"]
        return False, r.json().get("detail", "Invalid credentials")
    except Exception as e:
        return False, f"Backend connection error: {e}"

def get_watchlist(username):
    try:
        r = requests.get(f"{API_URL}/watchlist/{username}")
        if r.status_code == 200:
            return r.json().get("watchlist", [])
        return []
    except:
        return []

def add_to_watchlist(username, ticker):
    try:
        r = requests.post(f"{API_URL}/watchlist/add", json={"username": username, "ticker": ticker})
        return r.status_code == 200
    except:
        return False

def remove_from_watchlist(username, ticker):
    try:
        r = requests.post(f"{API_URL}/watchlist/remove", json={"username": username, "ticker": ticker})
        return r.status_code == 200
    except:
        return False

def get_portfolio(username):
    try:
        r = requests.get(f"{API_URL}/portfolio/{username}")
        if r.status_code == 200:
            return r.json().get("portfolio", [])
        return []
    except:
        return []

def buy_portfolio_item(username, ticker, shares, price):
    try:
        r = requests.post(f"{API_URL}/portfolio/buy", json={"username": username, "ticker": ticker, "shares": shares, "price": price})
        return r.status_code == 200
    except:
        return False

def sell_portfolio_item(username, ticker, shares, price=0):
    try:
        r = requests.post(f"{API_URL}/portfolio/sell", json={"username": username, "ticker": ticker, "shares": shares, "price": price})
        return r.status_code == 200
    except:
        return False
