import json
import requests
import time
from flask import Flask, request, jsonify

INSTRUMENT = "GBP_USD"
UNITS_FIXED = 1000
OANDA_ACCOUNT_ID = "101-001-39712262-001"
OANDA_TOKEN = "33728560a92939721c3b7b63edcec0a9-85dd3a8804ed0de506f5b3fe11c5c199"
OANDA_URL = "https://api-fxpractice.oanda.com"
URL_ORDER = f"https://api-fxpractice.oanda.com/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
URL_CLOSE = f"https://api-fxpractice.oanda.com/v3/accounts/{OANDA_ACCOUNT_ID}/positions/{INSTRUMENT}/close"

app = Flask(__name__)
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {OANDA_TOKEN}",
    "Content-Type": "application/json"
})

def place_order_institutional(units):
    payload = {
        "order": {
            "units": str(units),
            "instrument": INSTRUMENT,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {
                "distance": "150"
            },
            "takeProfitOnFill": {
                "distance": "300"
            }
        }
    }
    try:
        print(f"[TRANSMISIÓN] Enviando {units}...", flush=True)
        res = session.post(URL_ORDER, json=payload, timeout=10)
        print(f"[TELEMETRÍA] {res.status_code} {res.text[:400]}", flush=True)

        if res.status_code!= 201:
            return False

        return True
    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        return False

@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
def webhook_receiver():
    try:
        data = request.get_json(force=True, silent=True) or {}
        if data.get("secret") != "NEXUS_ALFA_99X":
            return jsonify({"status": "unauthorized"}), 401
        
        action = (data.get("action") or "").lower()
        print(f">>> CRUCE: {action.upper()} <<<", flush=True)

        if action == "buy":
            try:
                session.put(URL_CLOSE, json={"longUnits": "ALL", "shortUnits": "ALL"}, timeout=8)
                time.sleep(3)
            except:
                pass
            exito = place_order_institutional(UNITS_FIXED)
        elif action == "sell":
            try:
                session.put(URL_CLOSE, json={"longUnits": "ALL", "shortUnits": "ALL"}, timeout=8)
                time.sleep(1.5)
            except:
                pass
            exito = place_order_institutional(-UNITS_FIXED)
        else:
            return jsonify({"status": "ignored"}), 200

        if exito:
            return jsonify({"status": "executed", "action": action}), 200
        else:
            return jsonify({"status": "failed_at_broker"}), 502

    except Exception as e:
        print(f"💥 Error: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def index_check():
    return "=== [NEXUS ALFA V8.2 FIX] ACTIVO ==="

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)