-- Stock Market Predictor Database Schema
--
-- 1. New Tables
--    - stock_predictions: Stores ML predictions for stock trends
--    - stock_historical_data: Caches historical stock data
--
-- 2. Security
--    - Enable RLS on both tables
--    - Public read access for predictions
--
-- 3. Indexes
--    - Fast lookups by ticker and date

CREATE TABLE IF NOT EXISTS stock_predictions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker text NOT NULL,
  prediction_date timestamptz NOT NULL DEFAULT now(),
  next_day_trend text NOT NULL,
  confidence numeric,
  close_price numeric,
  open_price numeric,
  high_price numeric,
  low_price numeric,
  volume bigint,
  market_timezone text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stock_historical_data (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker text NOT NULL,
  date date NOT NULL,
  open numeric NOT NULL,
  high numeric NOT NULL,
  low numeric NOT NULL,
  close numeric NOT NULL,
  volume bigint NOT NULL,
  created_at timestamptz DEFAULT now(),
  UNIQUE(ticker, date)
);

ALTER TABLE stock_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_historical_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read predictions"
  ON stock_predictions FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can read historical data"
  ON stock_historical_data FOR SELECT
  TO anon
  USING (true);

CREATE INDEX IF NOT EXISTS idx_predictions_ticker_date 
  ON stock_predictions(ticker, prediction_date DESC);

CREATE INDEX IF NOT EXISTS idx_historical_ticker_date 
  ON stock_historical_data(ticker, date DESC);