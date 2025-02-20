import os
import logging
from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib
from waitress import serve
import json

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

BYBIT_API_KEY = os.environ.get("BYBIT_API_KEY")
BYBIT_API_SECRET = os.environ.get("BYBIT_API_SECRET")

if not BYBIT_API_KEY or not BYBIT_API_SECRET:
    raise ValueError("BYBIT_API_KEY veya BYBIT_API_SECRET ortam değişkenleri ayarlanmadı!")

def create_signature(params):
    """İmza oluşturma fonksiyonu."""
    secret_bytes = BYBIT_API_SECRET.encode('utf-8')
    params_bytes = params.encode('utf-8')
    sign = hmac.new(secret_bytes, params_bytes, hashlib.sha256).hexdigest()
    return sign

def get_bybit_balance():
    logging.info("get_bybit_balance fonksiyonu çağrıldı.")
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    params = f"api_key={BYBIT_API_KEY}&recv_window={recv_window}&timestamp={timestamp}"
    sign = create_signature(params)

    headers = {
        "X-BYBIT-API-KEY": BYBIT_API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window
    }

    url = "https://api-testnet.bybit.com/v5/account/wallet-balance"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        error_message = f"Bybit API hatası: {response.status_code}, {response.text}"
        logging.error(error_message)
        return jsonify({"error": error_message}), response.status_code

    try:
        bybit_response = response.json()
        if bybit_response.get("ret_code") == 0:
            result = bybit_response.get("result", {})
            usdt_balance = result.get("USDT", {}).get("available", 0)
            return {"balance": usdt_balance}
        else:
            error_message = bybit_response.get('ret_msg', 'Bilinmeyen Hata')
            logging.error(error_message)
            return jsonify({"error": error_message}), 500
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        error_message = f"Veri işleme hatası: {e}, {response.text}"
        logging.error(error_message)
        return jsonify({"error": error_message}), 500
    except Exception as e:
        error_message = f"Bilinmeyen bir hata oluştu: {e}, {response.text}"
        logging.error(error_message)
        return jsonify({"error": error_message}), 500

def place_bybit_order(symbol, side, qty, price):
    logging.info(f"place_bybit_order fonksiyonu çağrıldı: symbol={symbol}, side={side}, qty={qty}, price={price}")
    try:
        qty = float(qty) if qty is not None else None
        price = float(price) if price is not None else None
        if qty is None or price is None:
            return jsonify({"error": "qty veya price eksik veya hatalı"}), 400
    except ValueError:
        return jsonify({"error": "Geçersiz qty veya price formatı"}), 400

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    params = f"api_key={BYBIT_API_KEY}&symbol={symbol}&side={side}&order_type=Limit&qty={qty}&price={price}&time_in_force=GoodTillCancel&recv_window={recv_window}&timestamp={timestamp}"
    sign = create_signature(params)

    headers = {
        "X-BYBIT-API-KEY": BYBIT_API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window
    }

    url = "https://api-testnet.bybit.com/v5/order/create"  # Testnet URL'i
    response = requests.post(url, headers=headers, json={
        "symbol": symbol,
        "side": side,
        "order_type": "Limit",
        "qty": qty,
        "price": price,
        "time_in_force": "GoodTillCancel"
    })

    if response.status_code != 200:
        error_message = f"Bybit API hatası: {response.status_code}, {response.text}"
        logging.error(error_message)
        return jsonify({"error": error_message}), response.status_code

    try:
        bybit_response = response.json()
        if bybit_response.get("ret_code") == 0:
            order_id = bybit_response.get("result", {}).get("order_id")
            return jsonify({"success": True, "order_id": order_id})
        else:
            error_message = bybit_response.get("ret_msg", "Bilinmeyen bir hata")
            logging.error(f"Bybit API Hatası: {error_message}")
            return jsonify({"error": error_message}), 500
    except json.JSONDecodeError as e:
        error_message = f"JSONDecodeError: {e}, Response Text: {response.text}"
        logging.error(error_message)
        return jsonify({"error": "JSONDecodeError", "message": str(e)}), 500
    except Exception as e:
        error_message = f"Bilinmeyen bir hata oluştu: {e}, Response Text: {response.text}"
        logging.error(error_message)
        return jsonify({"error": "Bilinmeyen bir hata", "message": str(e)}), 500

@app.route("/")
def index():
    return "Merhaba Dünya! Bu benim ana sayfam!"

@app.route("/balance", methods=["GET"])
def get_balance():
    logging.info("/balance endpoint çağrıldı.")
    return get_bybit_balance()

@app.route("/tradingview", methods=["POST"])
def tradingview_webhook():
    logging.info("/tradingview endpoint çağrıldı.")
    data = request.get_json()
    if not data:
        return jsonify({"error": "Geçersiz JSON verisi"}), 400

    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")
    price = data.get("price")

    if not all([symbol, side, qty, price]):
        return jsonify({"error": "Eksik veri"}), 400

    order_response = place_bybit_order(symbol, side, qty, price)
    return order_response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    serve(app, host="0.0.0.0", port=port)
