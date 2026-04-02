import streamlit as st
import pandas as pd
import requests


# BASE_URL = "http://127.0.0.1:8000"
# BASE_URL = "http://backend:8000"
BASE_URL = "https://stock-intelligence-dashboard-d6qx.onrender.com/"
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Stock Intelligence Dashboard")


# SIDEBAR - COMPANY LIST

st.sidebar.title("Select Company")

companies = requests.get(f"{BASE_URL}/companies").json()

company_symbols = [c["Symbol"] for c in companies]

selected_company = st.sidebar.selectbox(
    "Choose a company",
    company_symbols
)


data = requests.get(f"{BASE_URL}/data/{selected_company}").json()
df = pd.DataFrame(data)

if df.empty:
    st.error("No data found")
    st.stop()

# convert date
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")


# FILTER OPTION

st.sidebar.markdown("### Filter Data")

filter_option = st.sidebar.selectbox(
    "Select Time Range",
    ["All", "Last 30 Days"]
)

if filter_option == "Last 30 Days":
    df = df.tail(30)


# MAIN LAYOUT

col1, col2 = st.columns([3, 1])


# CHART

with col1:
    st.subheader(f"{selected_company} Price Chart")
    st.line_chart(df.set_index("Date")["Close"])


# SUMMARY (FROM BACKEND)

summary = requests.get(f"{BASE_URL}/summary/{selected_company}").json()

with col2:
    st.subheader("📊 Summary")

    st.metric("52W High", round(summary["high_52w"], 2))
    st.metric("52W Low", round(summary["low_52w"], 2))
    st.metric("Average", round(summary["avg_close"], 2))

# ---------------------------
# 🤖 ML PREDICTION (FROM BACKEND)
# ---------------------------
st.subheader("🤖 Next Day Prediction")

pred = requests.get(f"{BASE_URL}/predict/{selected_company}").json()

if pred["prediction"]:
    st.success(f"Predicted Price: ₹ {pred['prediction']}")
else:
    st.error("Not enough data")

# ---------------------------
# 📊 COMPARE STOCKS
# ---------------------------
st.subheader("📊 Compare Stocks")

symbol2 = st.selectbox("Compare with", company_symbols)

if symbol2 and symbol2 != selected_company:
    compare_data = requests.get(
        f"{BASE_URL}/compare?symbol1={selected_company}&symbol2={symbol2}"
    ).json()

    df2 = pd.DataFrame(compare_data)

    df2["Date"] = pd.to_datetime(df2["Date"])

    pivot = df2.pivot(index="Date", columns="Symbol", values="Close")

    st.line_chart(pivot)

    # ---------------------------
    # 📊 CORRELATION (BONUS)
    # ---------------------------
    corr = requests.get(
        f"{BASE_URL}/correlation?symbol1={selected_company}&symbol2={symbol2}"
    ).json()

    st.info(f"Correlation: {corr['correlation']}")