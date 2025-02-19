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
    recv_window = "5000"
    params = f"api_key={API_KEY}&recv_window={recv_window}&timestamp={timestamp}"
    sign = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window
    }

    url = "https://api.bybit.com/v5/account/wallet-balance"
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

    url = "https://api.bybit.com/v5/order/create"
    response = requests.post(url, headers=headers, data=params)
    return response.json()
