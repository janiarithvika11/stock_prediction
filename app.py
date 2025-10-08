import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Stock Market Predictor 📈",
    page_icon="📊",
    layout="centered",
)

# -------------------- AUTO REFRESH --------------------
count = st_autorefresh(interval=60000, limit=None, key="auto_refresh")  # refresh every 60 sec

# -------------------- HEADER --------------------
st.title("📊 Smart Stock Market Predictor")
st.caption("Predict the **next day trend** using past stock performance 📅")

# -------------------- INPUT --------------------
ticker = st.text_input("Enter Stock Symbol (e.g., AAPL, INFY.NS, TCS.NS):", "AAPL")

if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

# -------------------- DATE AND TIME --------------------
now = datetime.datetime.now()
market_close = datetime.time(15, 30)
today = now.strftime("%A, %d %B %Y")
st.markdown(f"🗓️ **Today:** {today}")

# -------------------- FETCH HISTORICAL DATA --------------------
try:
    with st.spinner("Fetching latest stock data..."):
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if df.empty:
        st.error("Could not fetch stock data. Try another ticker.")
        df = None
except Exception as e:
    st.error(f"Error fetching stock data: {e}")
    df = None

if df is not None:
    # -------------------- FEATURE ENGINEERING --------------------
    df['Price_Change'] = df['Close'] - df['Open']
    df['High_Low'] = df['High'] - df['Low']
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA10'] = df['Close'].rolling(10).mean()
    df['Volume_Change'] = df['Volume'].pct_change()
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df.dropna(inplace=True)
# -------------------- CHECK IF MARKET OPEN --------------------
market_open = (now.weekday() < 5) and (now.time() < market_close)

if not market_open:
    if now.weekday() >= 5:
        st.warning("📅 Market is closed today (Weekend). Prediction skipped.")
    elif now.time() >= market_close:
        st.warning("⏰ Market has closed for the day (after 3:30 PM). Please check tomorrow.")
    else:
        st.warning("📅 Market holiday. Prediction skipped.")
    trend = None
    
else:
        # -------------------- MODEL TRAINING --------------------
    features = ['Close', 'High', 'Low', 'Open', 'Volume',
                'Price_Change', 'High_Low', 'MA5', 'MA10', 'Volume_Change']

    X = df[features]
    y = df['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # -------------------- NEXT DAY PREDICTION --------------------
    last_row = df.iloc[-1][features].values.reshape(1, -1)
    next_day_prediction = model.predict(last_row)[0]
    trend = "📈 UP" if next_day_prediction == 1 else "📉 DOWN"

    # -------------------- DISPLAY METRICS --------------------
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="📍 Stock Symbol", value=ticker.upper())
    with col2:
        st.metric(label="📅 Last Updated", value=datetime.datetime.now().strftime("%I:%M %p"))

    if trend:
        st.markdown("---")
        if trend == "📈 UP":
            st.success(f"### ✅ Predicted Market Trend for Next Day: **{trend}**")
        else:
            st.error(f"### ⚠️ Predicted Market Trend for Next Day: **{trend}**")
        st.markdown("---")

    # -------------------- CLOSING PRICE CHART --------------------
    with st.expander("📈 Closing Price Trend (Last 30 Days)"):
        recent_df = df.tail(30).copy()
        recent_df['Date'] = recent_df.index
        st.line_chart(recent_df.set_index('Date')['Close'])

    # -------------------- SHOW RECENT DATA --------------------
    with st.expander("📊 View Recent Stock Data (Last 5 Days)"):
        st.dataframe(df.tail(5))

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit & yFinance | by Simma Janiarithvika")
st.markdown("### Connect with me:")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)]"
        "(https://github.com/janiarithvika11)"
    )
with col2:
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)]"
        "(https://www.linkedin.com/in/janiarithvika-simma-ab07682b0/)"
    )
