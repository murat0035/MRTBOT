from flask import Flask, jsonify, request
import requests
import time
import hmac
import hashlib

# ✅ Flask Uygulamasını Başlat
app = Flask(__name__)

# ✅ BingX API Bilgileri (GÜVENLİK İÇİN .env DOSYASINA TAŞIYIN)
API_KEY = "YOUR_BINGX_API_KEY"
API_SECRET = "YOUR_BINGX_SECRET_KEY"
BASE_URL = "https://open-api.bingx.com"

# ✅ Sunucu Saatini Al (Doğru Timestamp)
def get_server_time():
    timestamp = int(time.time() * 1000)  # ✅ UNIX Timestamp (milisaniye cinsinden)
    return timestamp

# ✅ API Signature Hesapla
def generate_signature(params):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

# ✅ API İsteği Gönderme Fonksiyonu
def send_request(method, endpoint, params=None):
    if params is None:
        params = {}

    params["timestamp"] = get_server_time()  # ✅ Doğru timestamp ekleniyor
    params["signature"] = generate_signature(params)

    url = f"{BASE_URL}{endpoint}"
    headers = {
        "X-BX-APIKEY": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params)
        else:
            return {"error": "Invalid HTTP Method"}

        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ✅ Sunucu IP Adresini Göster
@app.route('/server/ip', methods=['GET'])
def get_server_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        ip_address = response.json().get("ip", "Bilinmeyen IP")
        return jsonify({"server_ip": ip_address})
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Sunucu Saatini Göster
@app.route('/server/time', methods=['GET'])
def server_time():
    return jsonify({"server_time": get_server_time()})

# ✅ BingX Hesap Bakiyesini Getir
@app.route('/account/balance', methods=['GET'])
def account_balance():
    return jsonify(send_request("GET", "/v1/user/getBalance"))

# ✅ Piyasa Fiyatını Getir
@app.route('/market/price', methods=['GET'])
def market_price():
    symbol = request.args.get("symbol", "BTCUSDT")  # Default olarak BTCUSDT kullan
    return jsonify(send_request("GET", "/v1/market/getPrice", {"symbol": symbol}))

# ✅ Limit Emir Gönder
@app.route('/trade/order', methods=['POST'])
def trade_order():
    data = request.json
    symbol = data.get("symbol", "BTCUSDT")
    side = data.get("side", "BUY")
    quantity = data.get("quantity", "0.01")
    price = data.get("price", "50000")

    params = {
        "symbol": symbol,
        "side": side,
        "orderType": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": "GTC"
    }
    return jsonify(send_request("POST", "/v1/trade/order", params))

# ✅ Flask Uygulamasını Çalıştır
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
