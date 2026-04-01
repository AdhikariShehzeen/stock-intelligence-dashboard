import pandas as pd
from sqlalchemy import create_engine

# connect to DB
engine = create_engine("sqlite:///./data/stocks.db")
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./data/stocks.db")

def create_table():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stock_data (
                Date TEXT,
                Open REAL,
                High REAL,
                Low REAL,
                Close REAL,
                Volume REAL,
                Symbol TEXT,
                Company TEXT,
                daily_return REAL,
                ma_7 REAL,
                volatility REAL,
                PRIMARY KEY (Date, Symbol)
            )
        """))

def save_to_db(df):
    create_table()
    df = df.drop(columns=["Dividends", "Stock Splits"], errors="ignore")
    df.fillna(0, inplace=True)
    df["Date"] = df["Date"].astype(str)
    df.drop_duplicates(subset=["Date", "Symbol"], inplace=True)

    # Insert in chunks
    df.to_sql(
        "stock_data",
        engine,
        if_exists="append",
        index=False,
        chunksize=100
    )
    print("Data saved to database!!!!!!")