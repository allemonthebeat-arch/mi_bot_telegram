import os
import requests
from flask import Flask

app = Flask(__name__)

# Configuración de tu Bot de Telegram
TOKEN = "8617996721:AAEwD0nvkhxfEG5im070OgRTtKZIUY6zS3s"
CHAT_ID = "7486041480"

def obtener_tasa_binance():
    try:
        url = "https://ve.dolarapi.com/v1/dolares/paralelo"
        response = requests.get(url, timeout=5)
        data = response.json()
        # Sumamos 32 bolívares para tener la tasa real de tu Binance P2P
        tasa_real_binance = float(data["promedio"]) + 32
        return f"{tasa_real_binance:.2f}"
    except Exception as e:
        print("Error obteniendo tasa:", e)
        return "863.02"  # Tasa de respaldo si falla la API

def enviar_mensaje_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Error enviando a Telegram:", e)

@app.route('/')
def home():
    # 1. Obtenemos la tasa en tiempo real de una vez
    tasa = obtener_tasa_binance()
    
    # 2. Le mandamos el mensaje a tu Telegram
    mensaje = f"TASA BINANCE P2P: {tasa}"
    enviar_mensaje_telegram(mensaje)
    
    # 3. Le respondemos a Google Sheets solo con el número
    return str(tasa), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
