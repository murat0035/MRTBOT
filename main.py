import requests
import time
import hmac
import hashlib
import json

class BingXAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://open-api.bingx.com"  # ✅ BingX API Base URL

    # ✅ Sunucu IP Adresini Al ve Yazdır
    def print_server_ip(self):
        try:
            response = requests.get("https://api64.ipify.org?format=json")
            ip_address = response.json().get("ip", "Bilinmeyen IP")
            print(f"📌 Sunucunun IP Adresi: {ip_address}")
        except Exception as e:
            print(f"⚠️ IP adresi alınamadı: {e}")

    # ✅ Sunucu Saatini Yazdır ve Doğru Timestamp Kullan
    def get_server_time(self):
        timestamp = int(time.time() * 1000)  # ✅ UNIX Timestamp (milisaniye cinsinden)
        print(f"📌 Sunucu Saati: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC")
        print(f"📌 Timestamp (ms): {timestamp}")
        return timestamp

    # ✅ İmza (Signature) Oluşturma
    def generate_signature(self, params):
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        signature = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        return signature

    # ✅ API İsteklerini Gönderme İşlemi
    def send_request(self, method, endpoint, params=None):
        if params is None:
            params = {}
        params["timestamp"] = self.get_server_time()  # ✅ Doğru timestamp kullanılıyor
        params["signature"] = self.generate_signature(params)

        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-BX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=params)
            else:
                raise ValueError("Geçersiz HTTP metodu")

            print(f"🔍 API Yanıt Kodu: {response.status_code}")
            print(f"🔍 API Yanıtı: {response.text}")

            return response.json()
        except Exception as e:
            print(f"❌ API İsteği Başarısız: {e}")
            return None

    # ✅ Hesap Bakiyesini Al (DOĞRU ENDPOINT KULLANILIYOR)
    def get_account_balance(self):
        return self.send_request("GET", "/v1/user/getBalance")

    # ✅ Piyasa Fiyatını Al (DOĞRU ENDPOINT KULLANILIYOR)
    def get_market_price(self, symbol):
        return self.send_request("GET", "/v1/market/getPrice", {"symbol": symbol})

    # ✅ Limit Emir Gönder (DOĞRU ENDPOINT KULLANILIYOR)
    def place_order(self, symbol, side, qty, price):
        params = {
            "symbol": symbol,
            "side": side,
            "orderType": "LIMIT",
            "quantity": qty,
            "price": price,
            "timeInForce": "GTC"  # Good Till Cancel
        }
        return self.send_request("POST", "/v1/trade/order", params)

# ✅ API Kullanımı
API_KEY = "EK7Om3CNprZDssrHO5Re4UayBvhlGUOhfpZoU7lBnwupWFNWmlXIZHpGH9cAPoKUpEZ2VcuMBurF03BezapA"  # 🔹 BingX API Key (Güvenlik için .env kullanılabilir)
API_SECRET = "oGykNZFCV6h0eHVLlrvUcULMcrGyv7yc6MdX03smUQS3mffZWbSWIutr8xSNcuHE072r8seMtsjKbBP3NkKLA"  # 🔹 BingX Secret Key

bingx = BingXAPI(API_KEY, API_SECRET)

# 📌 1️⃣ Sunucu IP Adresini Yazdır
bingx.print_server_ip()

# 📌 2️⃣ Sunucu Saatini Kontrol Et ve Senkronize Et
bingx.get_server_time()

# 📌 3️⃣ Hesap Bakiyesini Al (DÜZELTİLDİ)
balance = bingx.get_account_balance()
print(json.dumps(balance, indent=4))

# 📌 4️⃣ Piyasa Fiyatını Al (BTCUSDT) (DÜZELTİLDİ)
ticker = bingx.get_market_price("BTCUSDT")
print(json.dumps(ticker, indent=4))

# 📌 5️⃣ Limit Emir Gönder (BTCUSDT, BUY, 0.01 BTC, 50000 USDT fiyatında) (DÜZELTİLDİ)
order = bingx.place_order("BTCUSDT", "BUY", "0.01", "50000")
print(json.dumps(order, indent=4))
