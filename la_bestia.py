import json
import requests
from flask import Flask, request, jsonify

INSTRUMENT = "GBP_USD"
UNITS_FIXED = 1000
OANDA_ACCOUNT_ID = "001-001-21796206-001"
OANDA_TOKEN = "66295f6389690cf5a35a01b1756f25ce-48eaead5b5487821fb87a7eeebdb355e"

# ENDPOINT CRÍTICO OFICIAL DE LA API REST V20 VALIDADO POR GROK
URL_ORDER = f"https://api-fxpractice.oanda.com/v3/accounts/{OANDA_ACCOUNT_ID}/orders"

app  :  Flask(__name__)

# SESIÓN PERSISTENTE CORPORATIVA PARA SEPARAR EL TRÁFICO DE LA WEB COMERCIAL
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {OANDA_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Connection": "keep-alive"
})

def place_order_institutional(units):
    payload = {
        "order": {
            "units": str(units),
            "instrument": INSTRUMENT,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    try:
        print(f"[TRANSMISIÓN] Enviando orden lineal a OANDA por canal de API oficial...", flush=True)
        res = session.post(URL_ORDER, json=payload, timeout=8)
        print(f"[TELEMETRÍA] Código de Respuesta del Bróker: {res.status_code}", flush=True)
        print(f"[TELEMETRÍA] Respuesta Cruda: {res.text[:200]}", flush=True)
        
        if res.status_code == 201:
            print(">>>>> TARGET ENGAGED: ÓRDEN EJECUTADA EXITOSAMENTE <<<<<", flush=True)
            return True
        else:
            print(f"⚠️ OANDA RECHAZÓ LA SOLICITUD: {res.text}", flush=True)
            return False
    except Exception as e:
        print(f"❌ Error crítico de red conectando con el endpoint de OANDA: {e}", flush=True)
        return False

@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
def webhook_receiver():
    try:
        data = request.get_json(force=True)
        if data.get("secret") == "NEXUS_ALFA_99X":
            action = data.get("action")
            print(f">>> CRUCE CONFIRMADO EN RADAR TRADINGVIEW: {action.upper()} <<<", flush=True)
            
        if action == "buy":
            exito = place_order_institutional(UNITS_FIXED)
        elif action == "sell":
            exito = place_order_institutional(-UNITS_FIXED)
        else:
            return jsonify({"status": "ignored", "reason": "unknown_action"}), 200
                
        if exito:
            return jsonify({"status": "executed", "action": action}), 200
        else:
            return jsonify({"status": "failed_at_broker"}), 500
    except Exception as e:
        print(f"💥 Error interno procesando el paquete: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def index_check():
    return "=== [NEXUS ALFA V7.0] TOYOTA AVALON INMORTAL ACTIVO EN RENDER ==="
if __name__ == "__main__":
    app.run(port=10000)

