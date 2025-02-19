from flask import Flask, request, jsonify
import os
from pybit.unified_trading import HTTP

app = Flask(__name__)

session = HTTP(
    api_key="MdAeXSsw8CQgRoUN1o",
    api_secret="ijwrgCRYl3OwOHjbCyUgbfLfdQWtqPys2QcM",
)

@app.route("/")
def home():
    return "TradingView Bybit Bot Çalışıyor!"

@app.route("/bybit-balance", methods=["GET"])
def get_balance():
    try:
        balance = session.get_wallet_balance(accountType="UNIFIED")
        return jsonify(balance)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/check-keys", methods=["GET"])
def check_keys():
    return jsonify({
        "BYBIT_API_KEY": os.environ.get("BYBIT_API_KEY"),
        "BYBIT_API_SECRET": os.environ.get("BYBIT_API_SECRET")
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
