import os
import time
import requests
import hmac
import hashlib
from flask import Flask, request
from threading import Thread
import telebot
from dotenv import load_dotenv
from datetime import datetime

# ------------------- Cargar variables de entorno -------------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY")
BASE_URL = 'https://api.mexc.com'

bot = telebot.TeleBot(TOKEN)

# ------------------- Fondo 1: Fondo de Recuperación (MEXC API) -------------------
CACHE_TIMEOUT = 60  # segundos
_last_update_time = 0
_cached_fondo1_total = 0.0

inversores_f1 = [
    {"codigo": "123456", "nombre": "Varela", "porcentaje": 30.47},
    {"codigo": "654321", "nombre": "Ander",  "porcentaje": 45.30},
    {"codigo": "789012", "nombre": "Churri", "porcentaje": 13.02},
    {"codigo": "345678", "nombre": "Bruno",  "porcentaje": 2.17},
    {"codigo": "901234", "nombre": "Oli",    "porcentaje": 3.83},
    {"codigo": "567890", "nombre": "James",  "porcentaje": 5.19},
]

def get_fondo1_total():
    global _last_update_time, _cached_fondo1_total
    now = time.time()
    if now - _last_update_time > CACHE_TIMEOUT:
        path = '/api/v3/account'
        timestamp = int(now * 1000)
        query_string = f'timestamp={timestamp}'
        signature = hmac.new(MEXC_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        headers = { 'X-MEXC-APIKEY': MEXC_API_KEY }
        url = f'{BASE_URL}{path}?{query_string}&signature={signature}'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            total = 0.0
            for balance in data['balances']:
                amount = float(balance['free']) + float(balance['locked'])
                if amount > 0:
                    asset = balance['asset']
                    if asset == 'USDT':
                        total += amount  # No necesita conversión
                    else:
                        symbol = asset + 'USDT'
                        try:
                            price_url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
                            price_response = requests.get(price_url)
                            price_data = price_response.json()
                            price = float(price_data['price'])
                            total += amount * price
                        except:
                            continue
            _cached_fondo1_total = total
            _last_update_time = now
    return _cached_fondo1_total

# ------------------- Fondo 2: Pestillo Capital -------------------
FONDO2_TOTAL = 80000.0
DIVIDENDO_70 = 56000.0
DIVIDENDO_30 = 24000.0

aportes_f2 = {
    "Javi": 0.033185225,
    "Pata": 0.030886156,
    "Chuchi": 0.030071463,
    "Viadero": 0.012998077,
    "James": 0.0145053,
    "Pando": 0.010807289,
    "Rafa": 0.01075367,
    "Varo": 0.009405263,
    "Nando": 0.0088073,
    "Truchi": 0.00661272,
    "Bruno": 0.005107879,
    "Churri": 0.002013753,
    "Nani": 0.001783606,
    "Guille": 0.001675975,
}

total_btc_f2 = sum(aportes_f2.values())
kush_names = {"javi", "pata", "rafa"}
kush_fixed_div = DIVIDENDO_30 / len(kush_names)

inversores_f2 = []
for nombre, btc in aportes_f2.items():
    participacion = (btc / total_btc_f2) * 100
    div_normal = (participacion / 100) * DIVIDENDO_70
    div_kush = kush_fixed_div if nombre.lower() in kush_names else 0.0
    total_div = div_normal + div_kush
    inversores_f2.append({
        "nombre": nombre,
        "participacion": participacion,
        "div_normal": round(div_normal, 2),
        "div_kush": round(div_kush, 2),
        "total": round(total_div, 2)
    })

# ------------------- Comandos de tablas -------------------
@bot.message_handler(commands=['tabla1'])
def enviar_tabla1(message):
    fondo1_total = get_fondo1_total()
    tabla = "📋 Fondo de Recuperación\n\n"
    tabla += f"{'Código':<8} {'Nombre':<10} {'%':>7} {'Monto USD':>12}\n"
    tabla += "-" * 40 + "\n"
    for inv in sorted(inversores_f1, key=lambda x: x['porcentaje'], reverse=True):
        monto = round((inv["porcentaje"] / 100) * fondo1_total, 2)
        tabla += f"{inv['codigo']:<8} {inv['nombre']:<10} {inv['porcentaje']:>7.2f}%  ${monto:>11,.2f}\n"
    tabla += "-" * 40 + "\n"
    tabla += f"{'Total':<20} {100.00:>7.2f}%  ${fondo1_total:>11,.2f}\n"
    bot.send_message(message.chat.id, f"```\n{tabla}```", parse_mode='Markdown')

@bot.message_handler(commands=['tabla2'])
def enviar_tabla2(message):
    tabla = "📋 Pestillo Capital\n\n"
    tabla += f"{'Nombre':<10} {'%':>7} {'Dividendo $':>14} {'Div. Kush $':>13} {'Total $':>12}\n"
    tabla += "-" * 60 + "\n"
    for inv in sorted(inversores_f2, key=lambda x: x['participacion'], reverse=True):
        tabla += f"{inv['nombre']:<10} {inv['participacion']:>7.2f}%   ${inv['div_normal']:>12,.2f}   ${inv['div_kush']:>11,.2f}   ${inv['total']:>10,.2f}\n"
    tabla += "-" * 60 + "\n"
    tabla += f"{'TOTAL':<10} {100.00:>7.2f}%   ${DIVIDENDO_70:>12,.2f}   ${DIVIDENDO_30:>11,.2f}   ${FONDO2_TOTAL:>10,.2f}"
    bot.send_message(message.chat.id, f"```{tabla}```", parse_mode='Markdown')

# ------------------- Comando de últimas órdenes -------------------
@bot.message_handler(commands=['ordenes'])
def ultimas_ordenes(message):
    symbols = ['WIFUSDT', 'SOLUSDT', 'LDOUSDT','JTOUSDT','ETHUSDT','BTCUSDT']  # Agrega más si quieres
    timestamp = int(time.time() * 1000)
    query_string = f'timestamp={timestamp}'
    signature = hmac.new(MEXC_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    headers = {'X-MEXC-APIKEY': MEXC_API_KEY}
    
    respuesta = "🧾 Últimas órdenes del fondo:\n\n"
    for symbol in symbols:
        try:
            url = f"{BASE_URL}/api/v3/allOrders?symbol={symbol}&{query_string}&signature={signature}"
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()[-3:]
                if not data:
                    respuesta += f"📈 {symbol}: No hay órdenes.\n\n"
                    continue
                respuesta += f"📈 {symbol}:\n"
                for orden in data:
                    tipo = "🟢 COMPRA" if orden['side'] == 'BUY' else "🔴 VENTA"
                    estado = orden['status']
                    precio = orden['price']
                    cantidad = orden['origQty']
                    fecha = datetime.fromtimestamp(int(orden['time'])/1000).strftime('%Y-%m-%d %H:%M')
                    respuesta += f"{tipo} | {cantidad} @ {precio} | {estado} | {fecha}\n"
                respuesta += "\n"
        except Exception as e:
            respuesta += f"⚠️ Error al obtener {symbol}: {e}\n\n"
    bot.send_message(message.chat.id, respuesta.strip())

    # ------------------- Consulta individual -------------------

@bot.message_handler(func=lambda message: True)
def responder(message):
    nombre_input = message.text.strip().lower()
    total_general = 0.0
    respuesta = ""

    inv1 = next((inv for inv in inversores_f1 if inv['nombre'].lower() == nombre_input), None)
    if inv1:
        porcentaje1 = inv1["porcentaje"]
        monto1 = round((porcentaje1 / 100) * FONDO1_TOTAL, 2)
        total_general += monto1
        respuesta += (
            f"📌 Fondo de Recuperación\n"
            f"👤 Nombre: {inv1['nombre']}\n"
            f"📊 Participación: {porcentaje1:.2f}%\n"
            f"💰 Monto: ${monto1:,.2f} USD\n\n"
        )

    inv2 = next((inv for inv in inversores_f2 if inv['nombre'].lower() == nombre_input), None)
    if inv2:
        total_general += inv2["total"]
        respuesta += (
            f"📌 Pestillo Capital\n"
            f"👤 Nombre: {inv2['nombre']}\n"
            f"📊 Participación: {inv2['participacion']:.2f}%\n"
            f"💵 Dividendo: ${inv2['div_normal']:,.2f}\n"
            f"🍃 Dividendo KUSH: ${inv2['div_kush']:,.2f}\n"
            f"💰 Total Fondo 2: ${inv2['total']:,.2f} USD\n\n"
        )

    if respuesta:
        respuesta += f"📦 Total combinado: ${total_general:,.2f} USD"
        bot.reply_to(message, respuesta.strip(), parse_mode='Markdown')
    else:
        mensaje_bienvenida = """👋 ¡Bienvenido al canal de participación de fondos!

Estimado inversor,  
Gracias por formar parte de este espacio privado donde podrás consultar tu participación actualizada en dos fondos de inversión gestionados de forma independiente:

1. Fondo de Recuperación  
2. Pestillo Capital

📊 Aquí podrás consultar:
- Tu participación total (sumando ambos fondos).
- La distribución exacta de tus participaciones en cada fondo.

🔎 Escribe en el chat:
- ✅ Tu nombre completo para ver tu participación total.
- 📄 /tabla1 para ver la tabla del Fondo de Recuperación.
- 📄 /tabla2 para ver la tabla del Fondo Pestillo Capital.

Cualquier duda, no dudes en ponerte en contacto con la administración.  
¡Gracias por tu confianza y participación!"""
        bot.reply_to(message, mensaje_bienvenida, parse_mode='Markdown')


# ------------------- Servidor Flask -------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot activo!"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
