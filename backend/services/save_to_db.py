import pandas as pd
from sqlalchemy import create_engine, text

# connect to DB
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
    
    # Clean DataFrame
    df = df.drop(columns=["Dividends", "Stock Splits"], errors="ignore")
    df.fillna(0, inplace=True)
    df["Date"] = df["Date"].astype(str)
    df = df.drop_duplicates(subset=["Date", "Symbol"])
    
    # --- Filter out rows already in DB ---
    try:
        existing_df = pd.read_sql("SELECT Date, Symbol FROM stock_data", engine)
    except Exception:
        existing_df = pd.DataFrame(columns=["Date", "Symbol"])
    
    df_to_insert = df.merge(existing_df, on=["Date", "Symbol"], how="left", indicator=True)
    df_to_insert = df_to_insert[df_to_insert["_merge"] == "left_only"].drop(columns="_merge")

    if not df_to_insert.empty:
        df_to_insert.to_sql(
            "stock_data",
            engine,
            if_exists="append",
            index=False,
            chunksize=100
        )
        print(f"{len(df_to_insert)} new rows saved to database!")
    else:
        print("No new rows to insert. Database is already up-to-date.")
























