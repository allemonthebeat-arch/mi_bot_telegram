import os
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = "8617996721:AAEwD0nvkhxfEG5im070OgRTtKZIUY6zS3s"
CHAT_ID = "7486041480"

# Guardamos la última tasa enviada en memoria para comparar
ultima_tasa_enviada = None

def obtener_tasa_binance():
    try:
        url = "https://ve.dolarapi.com/v1/dolares/paralelo"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # SUMA TOTAL: 32 Bs (brecha original) + 10 Bs (ajuste nuevo) = 42 Bs
        tasa_real_binance = float(data["promedio"]) + 42
        
        return f"{tasa_real_binance:.2f}"
    except Exception as e:
        print("Error obteniendo tasa:", e)
        # Tasa de respaldo también ajustada con los 10 Bs extra (863.02 -> 873.02)
        return "873.02"

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
    global ultima_tasa_enviada
    tasa = obtener_tasa_binance()
    
    # Solo manda mensaje a Telegram si la tasa cambia de valor
    if tasa != ultima_tasa_enviada:
        mensaje = f"TASA BINANCE P2P: {tasa}"
        enviar_mensaje_telegram(mensaje)
        ultima_tasa_enviada = tasa  # Actualizamos el registro
    
    return str(tasa), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
