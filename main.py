from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = "MdAeXSsw8CQgRoUN1o"
SECRET_KEY = "ijwrgCRYl3OwOHjbCyUgbfLfdQWtqPys2QcM"

def bybit_balance():
    # API Bağlantı Testi
    test_url = "https://api-testnet.bybit.com/v5/market/time"
    test_response = requests.get(test_url)
    if test_response.status_code != 200:
        return {"error": "Bybit API'ye bağlanılamıyor", "response_text": test_response.text}

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # API İmzası oluşturma
    params = f"recv_window={recv_window}&timestamp={timestamp}"
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
        return {"error": f"Bybit API hatası: {response.status_code}", "response_text": response.text}
    
    try:
        return response.json()
    except Exception as e:
        return {"error": "JSONDecodeError", "message": str(e), "response_text": response.text}

def place_order(symbol, side, qty, price):
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
        return {"error": f"Bybit API hatası: {response.status_code}", "response_text": response.text}
    
    try:
        return response.json()
    except Exception as e:
        return {"error": "JSONDecodeError", "message": str(e), "response_text": response.text}

@app.route("/balance", methods=["GET"])
def get_balance():
    return jsonify(bybit_balance())

@app.route("/tradingview", methods=["POST"])
def tradingview_webhook():
    data = request.json
    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")
    price = data.get("price")
    
    order_response = place_order(symbol, side, qty, price)
    return jsonify(order_response)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)
