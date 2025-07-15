import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- Tu código de fondos, inversores y comandos (igual que antes) ---
# (Asegúrate de copiar todas las funciones de tu script original aquí, 
# sin la parte de infinity_polling ni keep_alive)

# Por ejemplo:

FONDO1_TOTAL = 15100.0
# ... (todo el código de fondos e inversores aquí) ...

@bot.message_handler(commands=['tabla1'])
def enviar_tabla1(message):
    # Tu función aquí
    pass

@bot.message_handler(commands=['tabla2'])
def enviar_tabla2(message):
    # Tu función aquí
    pass

@bot.message_handler(func=lambda message: True)
def responder(message):
    # Tu función aquí
    pass

# --- Endpoint webhook ---
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def home():
    return "Bot activo!"

if __name__ == "__main__":
    # Importante: elimina cualquier webhook previo antes de poner el nuevo
    bot.remove_webhook()
    # Cambia la URL a la tuya real, debe terminar en /webhook
    WEBHOOK_URL = "https://fondobot.onrender.com/webhook"
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host='0.0.0.0', port=8080)



