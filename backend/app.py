from flask import Flask, jsonify, request
from flask_cors import CORS
from services.stock_service import StockService
from services.prediction_service import PredictionService
from services.supabase_client import get_supabase_client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

stock_service = StockService()
prediction_service = PredictionService()
supabase = get_supabase_client()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Stock Market Predictor API'})

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        ticker = data.get('ticker', 'AAPL').upper()

        stock_data = stock_service.fetch_stock_data(ticker)
        if stock_data is None:
            return jsonify({'error': 'Could not fetch stock data'}), 400

        prediction_result = prediction_service.predict_next_day(stock_data, ticker)

        result = supabase.table('stock_predictions').insert({
            'ticker': ticker,
            'next_day_trend': prediction_result['trend'],
            'confidence': prediction_result.get('confidence'),
            'close_price': prediction_result['latest_data']['close'],
            'open_price': prediction_result['latest_data']['open'],
            'high_price': prediction_result['latest_data']['high'],
            'low_price': prediction_result['latest_data']['low'],
            'volume': int(prediction_result['latest_data']['volume']),
            'market_timezone': prediction_result['market_timezone']
        }).execute()

        return jsonify({
            'success': True,
            'ticker': ticker,
            'prediction': prediction_result['trend'],
            'confidence': prediction_result.get('confidence'),
            'market_status': prediction_result['market_status'],
            'latest_data': prediction_result['latest_data'],
            'timezone': prediction_result['market_timezone']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<ticker>', methods=['GET'])
def get_predictions(ticker):
    try:
        limit = request.args.get('limit', 10, type=int)

        result = supabase.table('stock_predictions').select('*').eq('ticker', ticker.upper()).order('prediction_date', desc=True).limit(limit).execute()

        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'predictions': result.data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/<ticker>', methods=['GET'])
def get_historical(ticker):
    try:
        days = request.args.get('days', 30, type=int)

        stock_data = stock_service.fetch_stock_data(ticker, period=f"{days}d")
        if stock_data is None:
            return jsonify({'error': 'Could not fetch historical data'}), 400

        historical_records = []
        for idx, row in stock_data.iterrows():
            historical_records.append({
                'ticker': ticker.upper(),
                'date': idx.date().isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })

        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'data': historical_records
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-status/<ticker>', methods=['GET'])
def market_status(ticker):
    try:
        status = stock_service.get_market_status(ticker)
        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'market_open': status['is_open'],
            'timezone': status['timezone'],
            'message': status['message']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
