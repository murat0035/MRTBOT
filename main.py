from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = "MdAeXSsw8CQgRoUN1o"
SECRET_KEY = "ijwrgCRYl3OwOHjbCyUgbfLfdQWtqPys2QcM"

def bybit_balance():
    timestamp = str(int(time.time() * 1000))
    params = ""
    sign = hmac.new(SECRET_KEY.encode(), (timestamp + API_KEY + params).encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp
    }

    url = "https://api.bybit.com/v5/account/wallet-balance"
    response = requests.get(url, headers=headers)
    return response.json()

def place_order(symbol, side, qty, price):
    timestamp = str(int(time.time() * 1000))
    params = f"symbol={symbol}&side={side}&order_type=Limit&qty={qty}&price={price}&time_in_force=GoodTillCancel"
    sign = hmac.new(SECRET_KEY.encode(), (timestamp + API_KEY + params).encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp
    }

    url = "https://api.bybit.com/v5/order/create"
    response = requests.post(url, headers=headers, data=params)
    return response.json()

a@app.route("/balance", methods=["GET"])
def get_balance():
    return jsonify(bybit_balance())

a@app.route("/tradingview", methods=["POST"])
def tradingview_webhook():
    data = request.json
    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")
    price = data.get("price")
    
    order_response = place_order(symbol, side, qty, price)
    return jsonify(order_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
