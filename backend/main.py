from fastapi import FastAPI
import pandas as pd
from sqlalchemy import create_engine, text


app = FastAPI(title="Stock Intelligence API")

# from fastapi.staticfiles import StaticFiles
# import os

# # Serve frontend
# frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
# app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# DB CONNECTION

engine = create_engine("sqlite:///./data/stocks.db")


# HOME

@app.get("/")
def home():
    return {"message": "Stock Intelligence Dashboard API is running!!!!!!!!!!!!1"}


# GET COMPANIES

@app.get("/companies")
def get_companies():
    print("hello!!!!!!!!!!!!!")
    query = """
        SELECT DISTINCT Symbol, Company
        FROM stock_data
        ORDER BY Symbol
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")



# GET LAST 30 DAYS DATA

@app.get("/data/{symbol}")
def get_stock_data(symbol: str):
    query = text("""
        SELECT *
        FROM stock_data
        WHERE Symbol = :symbol
        ORDER BY Date DESC
        LIMIT 30
    """)

    df = pd.read_sql(query, engine, params={"symbol": symbol.upper()})
    return df.to_dict(orient="records")



# SUMMARY (52-WEEK)

@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    query = text("""
        SELECT 
            MAX(Close) as high_52w,
            MIN(Close) as low_52w,
            AVG(Close) as avg_close
        FROM stock_data
        WHERE Symbol = :symbol
        AND Date >= date('now', '-365 day')
    """)

    df = pd.read_sql(query, engine, params={"symbol": symbol.upper()})
    return df.to_dict(orient="records")[0]



# COMPARE TWO STOCKS

@app.get("/compare")
def compare(symbol1: str, symbol2: str):
    query = text("""
        SELECT Date, Symbol, Close
        FROM stock_data
        WHERE Symbol IN (:s1, :s2)
        ORDER BY Date
    """)

    df = pd.read_sql(
        query,
        engine,
        params={"s1": symbol1.upper(), "s2": symbol2.upper()}
    )

    return df.to_dict(orient="records")


# ---------------------------
# 📊 CORRELATION (BONUS)
# ---------------------------
@app.get("/correlation")
def correlation(symbol1: str, symbol2: str):
    query = text("""
        SELECT Date, Symbol, Close
        FROM stock_data
        WHERE Symbol IN (:s1, :s2)
        ORDER BY Date
    """)

    df = pd.read_sql(
        query,
        engine,
        params={"s1": symbol1.upper(), "s2": symbol2.upper()}
    )

    if df.empty:
        return {"correlation": None}

    pivot = df.pivot(index="Date", columns="Symbol", values="Close")

    if symbol1.upper() not in pivot or symbol2.upper() not in pivot:
        return {"correlation": None}

    corr = pivot[symbol1.upper()].corr(pivot[symbol2.upper()])

    return {"correlation": round(float(corr), 4)}



# PREDICTION

@app.get("/predict/{symbol}")
def predict_price(symbol: str):
    query = text("""
        SELECT Close
        FROM stock_data
        WHERE Symbol = :symbol
        ORDER BY Date
    """)

    df = pd.read_sql(query, engine, params={"symbol": symbol.upper()})

    # not enough data
    if df.empty or len(df) < 5:
        return {"prediction": None}

    # simple trend-based prediction
    df["ma_5"] = df["Close"].rolling(5).mean()

    last_price = df["Close"].iloc[-1]
    last_ma = df["ma_5"].iloc[-1]

    prediction = last_price + (last_price - last_ma)

    return {
        "symbol": symbol.upper(),
        "prediction": round(float(prediction), 2)
    }

@app.get("/update-data")
def update_data():
    from backend.services.data_fetcher import main as fetch_data
    fetch_data()
    return {"message": "Data updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000)