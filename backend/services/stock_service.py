import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime, time

class StockService:
    def __init__(self):
        self.cache = {}

    def fetch_stock_data(self, ticker, period='6mo', interval='1d'):
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None

    def get_market_status(self, ticker):
        if ticker.endswith('.NS'):
            tz = pytz.timezone('Asia/Kolkata')
            market_close = time(15, 30)
            market_name = 'NSE'
        else:
            tz = pytz.timezone('America/New_York')
            market_close = time(16, 0)
            market_name = 'NYSE/NASDAQ'

        now = datetime.now(tz)
        is_weekend = now.weekday() >= 5
        is_after_close = now.time() >= market_close

        if is_weekend:
            return {
                'is_open': False,
                'timezone': str(tz),
                'message': f'{market_name} is closed (Weekend)'
            }
        elif is_after_close:
            return {
                'is_open': False,
                'timezone': str(tz),
                'message': f'{market_name} has closed for the day'
            }
        else:
            return {
                'is_open': True,
                'timezone': str(tz),
                'message': f'{market_name} is open'
            }

    def prepare_features(self, df):
        df = df.copy()
        df['Price_Change'] = df['Close'] - df['Open']
        df['High_Low'] = df['High'] - df['Low']
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['Volume_Change'] = df['Volume'].pct_change()
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        df.dropna(inplace=True)
        return df
