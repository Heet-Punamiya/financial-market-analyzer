import requests
import pandas as pd
import json
import time
from datetime import datetime
import io
from nsepython import *

def get_nse_stocks():
    """Fetch all NSE stocks from the official NSE master file"""
    stocks = {}

    try:
        print("Fetching NSE master file...")

        # NSE provides a master file with all listed securities
        url = "https://www.nseindia.com/api/equity-master"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market',
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        time.sleep(2)

        response = session.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                for stock in data['data']:
                    symbol = stock.get('symbol', '')
                    company_name = stock.get('companyName', '')
                    if symbol and company_name:
                        stocks[company_name] = f"{symbol}.NS"

        print(f"Found {len(stocks)} NSE stocks from master file")

        # If master file doesn't have all stocks, supplement with known major stocks
        if len(stocks) < 2000:
            print("Supplementing with comprehensive NSE stocks list...")
            # Add comprehensive list of NSE stocks
            nse_stocks_list = {
                "Reliance Industries Ltd": "RELIANCE.NS",
                "Tata Consultancy Services Ltd": "TCS.NS",
                "HDFC Bank Ltd": "HDFCBANK.NS",
                "ICICI Bank Ltd": "ICICIBANK.NS",
                "Infosys Ltd": "INFY.NS",
                "Hindustan Unilever Ltd": "HINDUNILVR.NS",
                "ITC Ltd": "ITC.NS",
                "Kotak Mahindra Bank Ltd": "KOTAKBANK.NS",
                "Larsen & Toubro Ltd": "LT.NS",
                "Bajaj Finance Ltd": "BAJFINANCE.NS",
                "HCL Technologies Ltd": "HCLTECH.NS",
                "Maruti Suzuki India Ltd": "MARUTI.NS",
                "Sun Pharmaceutical Industries Ltd": "SUNPHARMA.NS",
                "Bajaj Finserv Ltd": "BAJAJFINSV.NS",
                "NTPC Ltd": "NTPC.NS",
                "Axis Bank Ltd": "AXISBANK.NS",
                "Titan Company Ltd": "TITAN.NS",
                "ONGC Ltd": "ONGC.NS",
                "UltraTech Cement Ltd": "ULTRACEMCO.NS",
                "Asian Paints Ltd": "ASIANPAINT.NS",
                "Coal India Ltd": "COALINDIA.NS",
                "Tata Steel Ltd": "TATASTEEL.NS",
                "Power Grid Corporation of India Ltd": "POWERGRID.NS",
                "Nestle India Ltd": "NESTLEIND.NS",
                "Mahindra & Mahindra Ltd": "M&M.NS",
                "Wipro Ltd": "WIPRO.NS",
                "JSW Steel Ltd": "JSWSTEEL.NS",
                "Grasim Industries Ltd": "GRASIM.NS",
                "Hindalco Industries Ltd": "HINDALCO.NS",
                "Tech Mahindra Ltd": "TECHM.NS",
                "HDFC Life Insurance Company Ltd": "HDFCLIFE.NS",
                "Bajaj Auto Ltd": "BAJAJ-AUTO.NS",
                "Tata Consumer Products Ltd": "TATACONSUM.NS",
                "IndusInd Bank Ltd": "INDUSINDBK.NS",
                "Apollo Hospitals Enterprise Ltd": "APOLLOHOSP.NS",
                "Cipla Ltd": "CIPLA.NS",
                "Dr. Reddy's Laboratories Ltd": "DRREDDY.NS",
                "Hero MotoCorp Ltd": "HEROMOTOCO.NS",
                "Eicher Motors Ltd": "EICHERMOT.NS",
                "Divi's Laboratories Ltd": "DIVISLAB.NS",
                "BPCL Ltd": "BPCL.NS",
                "UPL Ltd": "UPL.NS",
                "Britannia Industries Ltd": "BRITANNIA.NS",
                "LTIMindtree Ltd": "LTIM.NS",
                "SBI Life Insurance Company Ltd": "SBILIFE.NS",
                "Adani Enterprises Ltd": "ADANIENT.NS",
                "Adani Ports and Special Economic Zone Ltd": "ADANIPORTS.NS",
                "Adani Green Energy Ltd": "ADANIGREEN.NS",
                "Adani Transmission Ltd": "ADANITRANS.NS",
                "Adani Total Gas Ltd": "ATGL.NS",
                "Adani Power Ltd": "ADANIPOWER.NS",
                "Zomato Ltd": "ZOMATO.NS",
                "Paytm": "PAYTM.NS",
                "Nykaa (FSN E-Commerce Ventures Ltd)": "NYKAA.NS",
                "State Bank of India": "SBIN.NS",
                "Hindustan Aeronautics Ltd": "HAL.NS",
                "GAIL (India) Ltd": "GAIL.NS",
                "Siemens Ltd": "SIEMENS.NS",
                "Pidilite Industries Ltd": "PIDILITIND.NS",
                "Dabur India Ltd": "DABUR.NS",
                "Shree Cement Ltd": "SHREECEM.NS",
                "Bajaj Holdings & Investment Ltd": "BAJAJHLDNG.NS",
                "Berger Paints India Ltd": "BERGEPAINT.NS",
                "Cholamandalam Investment and Finance Company Ltd": "CHOLAFIN.NS",
                "Godrej Consumer Products Ltd": "GODREJCP.NS",
                "Havells India Ltd": "HAVELLS.NS",
                "ICICI Lombard General Insurance Company Ltd": "ICICIGI.NS",
                "ICICI Prudential Life Insurance Company Ltd": "ICICIPRULI.NS",
                "InterGlobe Aviation Ltd": "INDIGO.NS",
                "Jindal Steel & Power Ltd": "JINDALSTEL.NS",
                "L&T Technology Services Ltd": "LTTS.NS",
                "MRF Ltd": "MRF.NS",
                "Page Industries Ltd": "PAGEIND.NS",
                "Petronet LNG Ltd": "PETRONET.NS",
                "Piramal Enterprises Ltd": "PEL.NS",
                "Procter & Gamble Hygiene and Health Care Ltd": "PGHH.NS",
                "SRF Ltd": "SRF.NS",
                "Torrent Pharmaceuticals Ltd": "TORNTPHARM.NS",
                "United Breweries Ltd": "UBL.NS",
                "United Spirits Ltd": "MCDOWELL-N.NS",
                "Varun Beverages Ltd": "VBL.NS",
                "Vedanta Ltd": "VEDL.NS",
                "Zee Entertainment Enterprises Ltd": "ZEEL.NS",
                "3M India Ltd": "3MINDIA.NS",
                "ABB India Ltd": "ABB.NS",
                "ACC Ltd": "ACC.NS",
                "AIA Engineering Ltd": "AIAENG.NS",
                "Ajanta Pharma Ltd": "AJANTPHARM.NS",
                "Alkem Laboratories Ltd": "ALKEM.NS",
                "Ambuja Cements Ltd": "AMBUJACEM.NS",
                "Apollo Tyres Ltd": "APOLLOTYRE.NS",
                "Ashok Leyland Ltd": "ASHOKLEY.NS",
                "Astral Ltd": "ASTRAL.NS",
                "Aurobindo Pharma Ltd": "AUROPHARMA.NS",
                "Balkrishna Industries Ltd": "BALKRISIND.NS",
                "Bandhan Bank Ltd": "BANDHANBNK.NS",
                "Bank of Baroda": "BANKBARODA.NS",
                "Bata India Ltd": "BATAINDIA.NS",
                "Bayer Cropscience Ltd": "BAYERCROP.NS",
                "BEL Ltd": "BEL.NS",
                "BEML Ltd": "BEML.NS",
                "Biocon Ltd": "BIOCON.NS",
                "Bosch Ltd": "BOSCHLTD.NS",
                "Crompton Greaves Consumer Electricals Ltd": "CROMPTON.NS",
                "Dalmia Bharat Ltd": "DALBHARAT.NS",
                "Deepak Nitrite Ltd": "DEEPAKNTR.NS",
                "EID Parry (India) Ltd": "EIDPARRY.NS",
                "Escorts Kubota Ltd": "ESCORTS.NS",
                "Exide Industries Ltd": "EXIDEIND.NS",
                "Federal Bank Ltd": "FEDERALBNK.NS",
                "Fortis Healthcare Ltd": "FORTIS.NS",
                "GMR Airports Infrastructure Ltd": "GMRINFRA.NS",
                "Godrej Industries Ltd": "GODREJIND.NS",
                "Godrej Properties Ltd": "GODREJPROP.NS",
                "Gujarat Gas Ltd": "GUJGASLTD.NS",
                "Hindustan Zinc Ltd": "HINDZINC.NS",
                "IDBI Bank Ltd": "IDBI.NS",
                "IDFC First Bank Ltd": "IDFCFIRSTB.NS",
                "Indian Oil Corporation Ltd": "IOC.NS",
                "Indian Railway Catering and Tourism Corporation Ltd": "IRCTC.NS",
                "Jubilant Foodworks Ltd": "JUBLFOOD.NS",
                "Kansai Nerolac Paints Ltd": "KANSAINER.NS",
                "Lupin Ltd": "LUPIN.NS",
                "Motherson Sumi Wiring India Ltd": "MSUMI.NS",
                "NMDC Ltd": "NMDC.NS",
                "Oberoi Realty Ltd": "OBEROIRLTY.NS",
                "PVR Ltd": "PVRINOX.NS",
                "Rajesh Exports Ltd": "RAJESHEXPO.NS",
                "RBL Bank Ltd": "RBLBANK.NS",
                "SBI Cards and Payment Services Ltd": "SBICARD.NS",
                "Shriram Transport Finance Company Ltd": "SRTRANSFIN.NS",
                "Supreme Industries Ltd": "SUPREMEIND.NS",
                "Tata Chemicals Ltd": "TATACHEM.NS",
                "Tata Communications Ltd": "TATACOMM.NS",
                "Tata Elxsi Ltd": "TATAELXSI.NS",
                "Tata Investment Corporation Ltd": "TATAINVEST.NS",
                "Tata Power Company Ltd": "TATAPOWER.NS",
                "TVS Motor Company Ltd": "TVSMOTOR.NS",
                "UPL Ltd": "UPL.NS",
                "Vodafone Idea Ltd": "IDEA.NS",
                "Voltas Ltd": "VOLTAS.NS",
                "Whirlpool of India Ltd": "WHIRLPOOL.NS",
                "Yes Bank Ltd": "YESBANK.NS",
                "Zydus Lifesciences Ltd": "ZYDUSLIFE.NS",
                # Add many more NSE stocks here...
            }
            stocks.update(nse_stocks_list)

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