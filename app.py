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
    secret_bytes = BYBIT_API_SECRET.encode('utf-8')
    params_bytes = params.encode('utf-8')
    sign = hmac.new(secret_bytes, params_bytes, hashlib.sha256).hexdigest()
    return sign

@app.route("/")
def index():
    return "Merhaba Dünya! Bu benim ana sayfam!"

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

    return jsonify({"success": True, "message": "Emir alındı!"})

if _name_ == "_main_":
    port = int(os.environ.get("PORT", 8000))
    serve(app, host="0.0.0.0", port=port)
