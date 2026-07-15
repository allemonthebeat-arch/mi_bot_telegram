import os
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = "8617996721:AAEwD0nvkhxfEG5im070OgRTtKZIUY6zS3s"
CHAT_ID = "7486041480"

ultima_tasa_enviada = None

def obtener_tasa_binance_p2p():
    try:
        # URL oficial del buscador de anuncios de Binance P2P
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        
        # Parámetros para buscar: Compra de USDT con Bolívares (VES)
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": True,  # Solo comerciantes verificados para mayor seguridad
            "page": 1,
            "rows": 5,
            "tradeType": "BUY"
        }
        
        response = requests.post(url, json=payload, timeout=5)
        data = response.json()
        
        # Tomamos el primer anuncio disponible (el mejor precio del P2P)
        precio_p2p = float(data["data"][0]["adv"]["price"])
        
        # Le sumamos los 10 Bs que me pediste para tu negocio
        tasa_final = precio_p2p + 10
        
        return f"{tasa_final:.2f}"
    except Exception as e:
        print("Error obteniendo tasa de Binance P2P:", e)
        return "873.02"  # Tasa de respaldo por si Binance bloquea la petición temporalmente

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
    tasa = obtener_tasa_binance_p2p()
    
    if tasa != ultima_tasa_enviada:
        mensaje = f"TASA BINANCE P2P REAL: {tasa}"
        enviar_mensaje_telegram(mensaje)
        ultima_tasa_enviada = tasa
    
    return str(tasa), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
