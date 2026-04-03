import yfinance as yf
import pandas as pd
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import save_to_db
# from . import save_to_db

COMPANIES = [
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","KOTAKBANK","SBIN","ITC","LT","AXISBANK",
    "ASIANPAINT","HINDUNILVR","BAJFINANCE","MARUTI","SUNPHARMA","TITAN","ULTRACEMCO",
    "NESTLEIND","POWERGRID","NTPC","ONGC","WIPRO","TECHM","ADANIENT","ADANIPORTS",
    "COALINDIA","JSWSTEEL","TATASTEEL","HCLTECH","GRASIM","BRITANNIA","INDUSINDBK",
    "CIPLA","EICHERMOT","HEROMOTOCO","DRREDDY","APOLLOHOSP","DIVISLAB","BAJAJFINSV",
    "HDFCLIFE","SBILIFE","ICICIPRULI","PIDILITIND","DABUR","GODREJCP","MARICO",
    "COLPAL","MUTHOOTFIN","AUROPHARMA","TORNTPHARM","LUPIN","ZYDUSLIFE","ALKEM",
    "BIOCON","ABB","SIEMENS","BHEL","HAVELLS","POLYCAB","DIXON","AMBUJACEM","ACC",
    "SHREECEM","DLF","OBEROIRLTY","GODREJPROP","IRCTC","ZOMATO","PAYTM","NYKAA",
    "TATAMOTORS","M&M","ASHOKLEY","TVSMOTOR","BPCL","HPCL","IOC","BANKBARODA",
    "PNB","CANBK","IDFCFIRSTB","FEDERALBNK","RBLBANK","GAIL","PETRONET","IGL",
    "VEDL","NMDC","SAIL","HAL","BEL"
]

COMPANY_MAP = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank"
}


company_cache = {}

def get_company_name(symbol, ticker):
    if symbol in company_cache:
        return company_cache[symbol]

    try:
        name = ticker.info.get("longName")
    except:
        name = None

    if not name:
        name = COMPANY_MAP.get(symbol, symbol)

    company_cache[symbol] = name
    return name



# --------------FETCH STOCK DATA---------------------

def fetch_stock(symbol):
    try:
        ticker_symbol = f"{symbol}.NS"  # NSE first
        ticker = yf.Ticker(ticker_symbol)

        df = ticker.history(period="1y")

        # fallback to BSE
        if df.empty:
            print(f"NSE failed, trying BSE for {symbol}")
            ticker_symbol = f"{symbol}.BO"
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(period="1y")

        if df.empty:
            print(f"No data for {symbol}")
            return None

        df.reset_index(inplace=True)
        df["Date"] = df["Date"].dt.tz_localize(None)
        # Add columns
        df["Symbol"] = symbol
        df["Company"] = get_company_name(symbol, ticker)


        #---------------------- METRICS---------------
        
        df["daily_return"] = (df["Close"] - df["Open"]) / df["Open"]
        df["ma_7"] = df["Close"].rolling(7).mean()
        df["volatility"] = df["Close"].rolling(7).std()

        return df

    except Exception as e:
        print(f"Error for {symbol}: {e}")
        return None



def main():
    all_data = []

    for symbol in COMPANIES:
        print(f"Fetching {symbol}...")
        df = fetch_stock(symbol)
        
        if df is not None:
            all_data.append(df)

        time.sleep(1)  # avoid rate limits

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        final_df.to_excel("stock_data.xlsx", index=False)
        save_to_db.save_to_db(final_df)
        print("Data saved to stock_data.xlsx")
        print(f"Total rows: {len(final_df)}")

    else:
        print("No data fetched")



if __name__ == "__main__":
    main()