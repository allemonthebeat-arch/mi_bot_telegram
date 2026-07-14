import os
import time
import threading
import requests
from flask import Flask

# 1. Configuración de Flask para Render (mantiene el bot "vivo")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo y corriendo", 200

# 2. Configuración de tu Bot de Telegram
TOKEN = "8617996721:AAEwD0nvkhxfEG5im070OgRTtKZIUY6zS3s"
CHAT_ID = "7486041480"

def obtener_tasa_binance():
    try:
        url = "https://ve.dolarapi.com/v1/dolares/paralelo"
        response = requests.get(url)
        data = response.json()
        # Sumamos 32 bolívares para tener la tasa real de tu Binance P2P
        tasa_real_binance = float(data["promedio"]) + 32
        return tasa_real_binance
    except Exception as e:
        print("Error obteniendo tasa:", e)
        return None

def enviar_mensaje_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error enviando a Telegram:", e)

# 3. El bucle infinito del bot corriendo en segundo plano
def bucle_bot():
    print("Bucle del bot iniciado...")
    while True:
        try:
            tasa = obtener_tasa_binance()
            if tasa:
                mensaje = f"TASA BINANCE P2P: {tasa:.2f}"
                enviar_mensaje_telegram(mensaje)
                print(f"Mensaje enviado con éxito: {tasa:.2f}")
        except Exception as e:
            print(f"Error en el bucle: {e}")
        
        # Espera 5 minutos (300 segundos)
        time.sleep(300)

# 4. Arrancar el bot en un hilo separado antes de iniciar Flask
bot_thread = threading.Thread(target=bucle_bot)
bot_thread.daemon = True
bot_thread.start()

if __name__ == "__main__":
    # Render asigna automáticamente un puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
