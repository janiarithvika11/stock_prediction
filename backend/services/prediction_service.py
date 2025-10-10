from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import pytz
from datetime import datetime, time

class PredictionService:
    def __init__(self):
        self.model = None

    def train_model(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        accuracy = self.model.score(X_test, y_test)
        return accuracy

    def predict_next_day(self, stock_data, ticker):
        df = stock_data.copy()

        df['Price_Change'] = df['Close'] - df['Open']
        df['High_Low'] = df['High'] - df['Low']
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['Volume_Change'] = df['Volume'].pct_change()
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        df.dropna(inplace=True)

        features = ['Close', 'High', 'Low', 'Open', 'Volume',
                    'Price_Change', 'High_Low', 'MA5', 'MA10', 'Volume_Change']

        X = df[features]
        y = df['Target']

        accuracy = self.train_model(X, y)

        last_row = df.iloc[-1][features].values.reshape(1, -1)
        prediction = self.model.predict(last_row)[0]
        trend = 'UP' if prediction == 1 else 'DOWN'

        if ticker.endswith('.NS'):
            tz = pytz.timezone('Asia/Kolkata')
            market_close = time(15, 30)
        else:
            tz = pytz.timezone('America/New_York')
            market_close = time(16, 0)

        now = datetime.now(tz)
        market_open = (now.weekday() < 5) and (now.time() < market_close)

        latest = df.iloc[-1]

        return {
            'trend': trend,
            'confidence': float(accuracy),
            'market_status': 'open' if market_open else 'closed',
            'market_timezone': str(tz),
            'latest_data': {
                'close': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume'])
            }
        }
