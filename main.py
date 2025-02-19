import os
import logging
from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib
from waitress import serve

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

API_KEY = os.environ.get("BYBIT_API_KEY")
SECRET_KEY = os.environ.get("BYBIT_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    logging.error("API_KEY veya SECRET_KEY ortam değişkenleri ayarlanmadı!")
    exit(1)

def bybit_balance():
    logging.info("bybit_balance fonksiyonu çağrıldı.")
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    params = f"api_key={API_KEY}&recv_window={recv_window}&timestamp={timestamp}"
    sign = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window
    }

    url = "https://api-testnet.bybit.com/v5/account/wallet-balance"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": f"Bybit API hatası: {response.status_code}", "response_text": response.text}), response.status_code

    try:
        return response.json()
    except Exception as e:
        return jsonify({"error": "JSONDecodeError", "message": str(e), "response_text": response.text}), 500

def place_order(symbol, side, qty, price):
    logging.info(f"place_order fonksiyonu çağrıldı: symbol={symbol}, side={side}, qty={qty}, price={price}")
    try:
        qty = float(qty)
        price = float(price)
    except ValueError:
        return jsonify({"error": "Geçersiz qty veya price formatı"}), 400

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    params = f"api_key={API_KEY}&symbol={symbol}&side={side}&order_type=Limit&qty={qty}&price={price}&time_in_force=GoodTillCancel&recv_window={recv_window}&timestamp={timestamp}"
    sign = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window
    }

    url = "https://api-testnet.bybit.com/v5/order/create"
    response = requests.post(url, headers=headers, json={"symbol": symbol, "side": side, "order_type": "Limit", "qty": qty, "price": price, "time_in_force": "GoodTillCancel"})

    if response.status_code != 200:
        return jsonify({"error": f"Bybit API hatası: {response.status_code}", "response_text": response.text}), response.status_code

    try:
        return response.json()
    except Exception as e:
        return jsonify({"error": "JSONDecodeError", "message": str(e), "response_text": response.text}), 500

@app.route("/balance", methods=["GET"])
def get_balance():
    logging.info("/balance endpoint çağrıldı.")
    return jsonify(bybit_balance())

@app.route("/tradingview", methods=["POST"])
def tradingview_webhook():
    logging.info("/tradingview endpoint çağrıldı.")
    data = request.json
    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")
    price = data.get("price")

    order_response = place_order(symbol, side, qty, price)
    return jsonify(order_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    serve(app, host="0.0.0.0", port=port)
