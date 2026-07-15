import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

# Variable global para guardar la última tasa calculada
ultima_tasa = "863.02"

@app.route('/')
def home():
    # Cuando Google Sheets entre aquí, verá la tasa limpia directamente
    return str(ultima_tasa), 200

TOKEN = "8617996721:AAEwD0nvkhxfEG5im070OgRTtKZIUY6zS3s"
CHAT_ID = "7486041480"

def obtener_tasa_binance():
    try:
        url = "https://ve.dolarapi.com/v1/dolares/paralelo"
        response = requests.get(url)
        data = response.json()
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

def bucle_bot():
    global ultima_tasa
    print("Bucle del bot iniciado...")
    while True:
        try:
            tasa = obtener_tasa_binance()
            if tasa:
                # Guardamos la tasa formateada
                ultima_tasa = f"{tasa:.2f}"
                mensaje = f"TASA BINANCE P2P: {ultima_tasa}"
                enviar_mensaje_telegram(mensaje)
                print(f"Mensaje enviado con éxito: {ultima_tasa}")
        except Exception as e:
            print(f"Error en el bucle: {e}")
        
        time.sleep(300)

bot_thread = threading.Thread(target=bucle_bot)
bot_thread.daemon = True
bot_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
