import streamlit as st
import pandas as pd
import requests



import requests


BASE_URL = "http://54.206.205.26:8000"

# try:
#     response = requests.get(f"{BASE_URL}/companies", timeout=5)

#     st.write("Status Code:", response.status_code)
#     st.write("Raw Response:", response.text[:200])  # debug

#     if response.status_code == 200:
#         companies = response.json()
#     else:
#         st.error("API failed")
#         companies = []

# except Exception as e:
#     st.error(f"Error: {e}")
#     companies = []

# =========================
# CONFIG
# =========================
# BASE_URL = "http://127.0.0.1:8000"
# BASE_URL = "http://54.206.205.26:8000"


st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Stock Intelligence Dashboard")

# =========================
# SAFE API FUNCTION
# =========================
def safe_api(url):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        return res.json()
    except:
        return None

# =========================
# SIDEBAR - COMPANY LIST
# =========================
st.sidebar.title("Select Company")

# st.write("Calling backend...")
# st.write("Hello")
# st.write("🚀 Calling backend from Streamlit...")

try:
    # res = requests.get("http://54.206.205.26:8000/companies", timeout=5)
    res = requests.get(f"{BASE_URL}/companies", timeout=5)
    # st.write("Status Code:", res.status_code)
    # st.write("Response Text:", res.text)

    companies = res.json()

    # st.write("Companies Parsed:", companies)

except Exception as e:
    st.error(f"❌ ERROR: {e}")
    st.stop()

if not companies:
    st.error("⚠️ Backend not responding (companies)")
    st.stop()


if companies:
    st.sidebar.write("Companies Loaded ✅")
company_symbols = [c["Symbol"] for c in companies]

selected_company = st.sidebar.selectbox(
    "Choose a company",
    company_symbols
)

# =========================
# FETCH DATA
# =========================
data = safe_api(f"{BASE_URL}/data/{selected_company}")

if not data:
    st.error("⚠️ No data found")
    st.stop()

df = pd.DataFrame(data)

if df.empty:
    st.error("⚠️ Empty dataset")
    st.stop()

# =========================
# DATA PROCESSING
# =========================
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# =========================
# FILTER
# =========================
st.sidebar.markdown("### Filter Data")

filter_option = st.sidebar.selectbox(
    "Select Time Range",
    ["All", "Last 30 Days"]
)

if filter_option == "Last 30 Days":
    df = df.tail(30)

# =========================
# MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

# =========================
# CHART
# =========================
with col1:
    st.subheader(f"{selected_company} Price Chart")
    st.line_chart(df.set_index("Date")["Close"])

# =========================
# SUMMARY
# =========================
summary = safe_api(f"{BASE_URL}/summary/{selected_company}")

with col2:
    st.subheader("📊 Summary")

    if summary:
        st.metric("52W High", round(summary["high_52w"], 2))
        st.metric("52W Low", round(summary["low_52w"], 2))
        st.metric("Average", round(summary["avg_close"], 2))
    else:
        st.warning("Summary not available")

# =========================
# ML PREDICTION
# =========================
st.subheader("🤖 Next Day Prediction")

pred = safe_api(f"{BASE_URL}/predict/{selected_company}")

if pred and pred.get("prediction"):
    st.success(f"Predicted Price: ₹ {pred['prediction']}")
else:
    st.warning("Prediction not available")

# =========================
# COMPARE STOCKS
# =========================
st.subheader("📊 Compare Stocks")

symbol2 = st.selectbox("Compare with", company_symbols)

if symbol2 and symbol2 != selected_company:
    compare_data = safe_api(
        f"{BASE_URL}/compare?symbol1={selected_company}&symbol2={symbol2}"
    )

    if compare_data:
        df2 = pd.DataFrame(compare_data)
        df2["Date"] = pd.to_datetime(df2["Date"])

        pivot = df2.pivot(index="Date", columns="Symbol", values="Close")
        st.line_chart(pivot)

        # =========================
        # CORRELATION
        # =========================
        corr = safe_api(
            f"{BASE_URL}/correlation?symbol1={selected_company}&symbol2={symbol2}"
        )

        if corr:
            st.info(f"Correlation: {corr['correlation']}")
        else:
            st.warning("Correlation not available")
    else:
        st.warning("Comparison data not available")