import yfinance as yf
import pandas as pd


def get_market_data():

    tickers = {
        "IHSG": "^JKSE",
        "BBCA": "BBCA.JK",
        "TLKM": "TLKM.JK"
    }

    results = {}

    for name, ticker in tickers.items():
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)

            if df.empty:
                results[name] = {
                    "trend": "Data tidak tersedia",
                    "confidence": "Rendah"
                }
                continue

            close = df["Close"]

            sma20 = close.rolling(20).mean()
            sma50 = close.rolling(50).mean()

            last_close = float(close.iloc[-1])
            last_sma20 = float(sma20.iloc[-1])
            last_sma50 = float(sma50.iloc[-1])

            if last_close > last_sma20 and last_sma20 > last_sma50:
                trend = "Uptrend"
                confidence = "Tinggi"
            elif last_close < last_sma20 and last_sma20 < last_sma50:
                trend = "Downtrend"
                confidence = "Tinggi"
            else:
                trend = "Sideways"
                confidence = "Sedang"

            results[name] = {
                "trend": trend,
                "confidence": confidence
            }

        except Exception as e:
            results[name] = {
                "trend": "Error",
                "confidence": "Rendah"
            }

    return results
