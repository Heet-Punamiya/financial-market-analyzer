import requests
import pandas as pd
import json
import time
from datetime import datetime
import io
from nsepython import *

def get_nse_stocks():
    """Fetch all NSE stocks from the official NSE archives CSV"""
    stocks = {}

    try:
        print("Fetching NSE master file from nsearchives...")
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            for idx, row in df.iterrows():
                symbol = str(row.get('SYMBOL', '')).strip()
                company_name = str(row.get('NAME OF COMPANY', '')).strip()
                if symbol and company_name:
                    stocks[company_name] = f"{symbol}.NS"
            print(f"Found {len(stocks)} NSE stocks from master file")
        else:
            print(f"Failed to fetch NSE master file, status code: {response.status_code}")

    except Exception as e:
        print(f"Error fetching NSE stocks: {e}")

    return stocks


def get_bse_stocks():
    """Fetch BSE stocks - using a simpler approach for now"""
    stocks = {}

    try:
        print("Fetching BSE stocks...")
        # For BSE, we can try to get major stocks or use a static list
        # BSE has around 5600 stocks, but getting all programmatically is complex

        # For now, let's add some major BSE stocks manually or from a known list
        major_bse_stocks = {
            "Reliance Industries Ltd": "RELIANCE.BO",
            "Tata Consultancy Services Ltd": "TCS.BO",
            "HDFC Bank Ltd": "HDFCBANK.BO",
            "ICICI Bank Ltd": "ICICIBANK.BO",
            "Infosys Ltd": "INFY.BO",
            "Hindustan Unilever Ltd": "HINDUNILVR.BO",
            "ITC Ltd": "ITC.BO",
            "Kotak Mahindra Bank Ltd": "KOTAKBANK.BO",
            "Larsen & Toubro Ltd": "LT.BO",
            "Bajaj Finance Ltd": "BAJFINANCE.BO",
            "HCL Technologies Ltd": "HCLTECH.BO",
            "Maruti Suzuki India Ltd": "MARUTI.BO",
            "Sun Pharmaceutical Industries Ltd": "SUNPHARMA.BO",
            "Bajaj Finserv Ltd": "BAJAJFINSV.BO",
            "NTPC Ltd": "NTPC.BO",
            "Axis Bank Ltd": "AXISBANK.BO",
            "Titan Company Ltd": "TITAN.BO",
            "ONGC Ltd": "ONGC.BO",
            "UltraTech Cement Ltd": "ULTRACEMCO.BO",
            "Asian Paints Ltd": "ASIANPAINT.BO",
            "Coal India Ltd": "COALINDIA.BO",
            "Tata Steel Ltd": "TATASTEEL.BO",
            "Power Grid Corporation of India Ltd": "POWERGRID.BO",
            "Nestle India Ltd": "NESTLEIND.BO",
            "Mahindra & Mahindra Ltd": "M&M.BO",
            "Wipro Ltd": "WIPRO.BO",
            "JSW Steel Ltd": "JSWSTEEL.BO",
            "Grasim Industries Ltd": "GRASIM.BO",
            "Hindalco Industries Ltd": "HINDALCO.BO",
            "Tech Mahindra Ltd": "TECHM.BO",
            "HDFC Life Insurance Company Ltd": "HDFCLIFE.BO",
            "Bajaj Auto Ltd": "BAJAJ-AUTO.BO",
            "Tata Consumer Products Ltd": "TATACONSUM.BO",
            "IndusInd Bank Ltd": "INDUSINDBK.BO",
            "Apollo Hospitals Enterprise Ltd": "APOLLOHOSP.BO",
            "Cipla Ltd": "CIPLA.BO",
            "Dr. Reddy's Laboratories Ltd": "DRREDDY.BO",
            "Hero MotoCorp Ltd": "HEROMOTOCO.BO",
            "Eicher Motors Ltd": "EICHERMOT.BO",
            "Divi's Laboratories Ltd": "DIVISLAB.BO",
            "BPCL Ltd": "BPCL.BO",
            "UPL Ltd": "UPL.BO",
            "Britannia Industries Ltd": "BRITANNIA.BO",
            "LTIMindtree Ltd": "LTIM.BO",
            "SBI Life Insurance Company Ltd": "SBILIFE.BO",
            "Adani Enterprises Ltd": "ADANIENT.BO",
            "Adani Ports and Special Economic Zone Ltd": "ADANIPORTS.BO",
            "State Bank of India": "SBIN.BO",
            "Hindustan Aeronautics Ltd": "HAL.BO",
            "GAIL (India) Ltd": "GAIL.BO",
            "Siemens Ltd": "SIEMENS.BO",
            "Pidilite Industries Ltd": "PIDILITIND.BO",
            "Dabur India Ltd": "DABUR.BO",
            "Shree Cement Ltd": "SHREECEM.BO",
            "Bajaj Holdings & Investment Ltd": "BAJAJHLDNG.BO",
            "Berger Paints India Ltd": "BERGEPAINT.BO",
            "Cholamandalam Investment and Finance Company Ltd": "CHOLAFIN.BO",
            "Godrej Consumer Products Ltd": "GODREJCP.BO",
            "Havells India Ltd": "HAVELLS.BO",
            "ICICI Lombard General Insurance Company Ltd": "ICICIGI.BO",
            "ICICI Prudential Life Insurance Company Ltd": "ICICIPRULI.BO",
            "InterGlobe Aviation Ltd": "INDIGO.BO",
            "Jindal Steel & Power Ltd": "JINDALSTEL.BO",
            "L&T Technology Services Ltd": "LTTS.BO",
            "MRF Ltd": "MRF.BO",
            "Page Industries Ltd": "PAGEIND.BO",
            "Petronet LNG Ltd": "PETRONET.BO",
            "Piramal Enterprises Ltd": "PEL.BO",
            "Procter & Gamble Hygiene and Health Care Ltd": "PGHH.BO",
            "SRF Ltd": "SRF.BO",
            "Torrent Pharmaceuticals Ltd": "TORNTPHARM.BO",
            "United Breweries Ltd": "UBL.BO",
            "United Spirits Ltd": "MCDOWELL-N.BO",
            "Varun Beverages Ltd": "VBL.BO",
            "Vedanta Ltd": "VEDL.BO",
            "Zee Entertainment Enterprises Ltd": "ZEEL.BO",
        }

        stocks.update(major_bse_stocks)
        print(f"Added {len(major_bse_stocks)} major BSE stocks")

    except Exception as e:
        print(f"Error fetching BSE stocks: {e}")

    return stocks

def update_stocks_file(nse_stocks, bse_stocks):
    """Update the indian_stocks.py file with new stocks"""
    # Combine NSE and BSE stocks
    all_stocks = {**nse_stocks, **bse_stocks}

    # Read current file
    try:
        with open('indian_stocks.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "ALL_STOCKS = {}"

    # Find the ALL_STOCKS dictionary and replace it
    start_marker = "ALL_STOCKS = {"
    end_marker = "}"

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Could not find ALL_STOCKS dictionary in file")
        return

    end_idx = content.find(end_marker, start_idx) + 1
    if end_idx == 0:
        print("Could not find end of ALL_STOCKS dictionary")
        return

    # Create new dictionary content
    stocks_lines = []
    for name, ticker in sorted(all_stocks.items()):
        stocks_lines.append(f'    "{name}": "{ticker}",')

    new_dict_content = "ALL_STOCKS = {\n" + "\n".join(stocks_lines) + "\n}"

    # Replace the old dictionary
    new_content = content[:start_idx] + new_dict_content + content[end_idx:]

    # Write back to file
    with open('indian_stocks.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Updated indian_stocks.py with {len(all_stocks)} stocks")

if __name__ == "__main__":
    print("Fetching NSE stocks...")
    nse_stocks = get_nse_stocks()
    print(f"Found {len(nse_stocks)} NSE stocks")

    print("Fetching BSE stocks...")
    bse_stocks = get_bse_stocks()
    print(f"Found {len(bse_stocks)} BSE stocks")

    if nse_stocks or bse_stocks:
        update_stocks_file(nse_stocks, bse_stocks)
    else:
        print("No stocks found to update")