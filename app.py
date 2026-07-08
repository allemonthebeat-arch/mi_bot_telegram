import os
import requests
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Configuración básica
logging.basicConfig(level=logging.INFO)

# Usamos variables de entorno para mayor seguridad (se configuran en Render)
TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Servidor web mínimo para que Render mantenga el proceso activo
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot activo")

def run_web():
    port = int(os.environ.get("PORT", 7860))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

async def start(update, context):
    await update.message.reply_text("Hola, estoy funcionando correctamente en Render.")

async def handle_message(update, context):
    user_text = update.message.text
    url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(url, headers=headers, json={"inputs": user_text}, timeout=10)
        if response.status_code == 200:
            respuesta = response.json()[0].get('generated_text', "No tengo respuesta")
            await update.message.reply_text(respuesta)
        else:
            await update.message.reply_text("Error al conectar con la IA.")
    except Exception as e:
        await update.message.reply_text("Ocurrió un error inesperado.")

if __name__ == '__main__':
    # Iniciar servidor web en segundo plano
    threading.Thread(target=run_web, daemon=True).start()
    
    # Iniciar bot
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot iniciando ejecución...")
    app.run_polling()
  
