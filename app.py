import os
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Tokens
TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Servidor de monitoreo optimizado para UptimeRobot
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# Función para obtener precio USDT en VES
def obtener_precio_usdt():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "BUY",
        "merchantCheck": True,
        "page": 1,
        "rows": 1
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            precio = response.json()['data'][0]['adv']['price']
            return f"💰 Precio actual USDT/VES en Binance: {precio} VES"
        return "No pude obtener el precio en este momento."
    except:
        return "Error consultando a Binance."

# Comandos del Bot
async def start(update, context):
    await update.message.reply_text("¡Hola! Soy tu bot de monitoreo. Escribe /precio para ver el costo del USDT.")

async def comando_precio(update, context):
    precio = obtener_precio_usdt()
    await update.message.reply_text(precio)

async def handle_message(update, context):
    user_text = update.message.text
    url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(url, headers=headers, json={"inputs": user_text})
    if response.status_code == 200:
        respuesta = response.json()[0].get('generated_text', "No tengo una respuesta para eso.")
        await update.message.reply_text(respuesta)

if __name__ == '__main__':
    # Inicia el servidor web en un hilo separado
    threading.Thread(target=run_web, daemon=True).start()
    
    # Inicia el Bot de Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("precio", comando_precio))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
    
