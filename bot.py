import os
import telebot
from flask import Flask
from threading import Thread
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Token de BotFather desde variable de entorno
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ------------------- Fondo 1: Fondo de Recuperación -------------------
FONDO1_TOTAL = 15100.0

inversores_f1 = [
    {"codigo": "123456", "nombre": "Varela", "porcentaje": 30.47},
    {"codigo": "654321", "nombre": "Ander",  "porcentaje": 45.30},
    {"codigo": "789012", "nombre": "Churri", "porcentaje": 13.02},
    {"codigo": "345678", "nombre": "Bruno",  "porcentaje": 2.17},
    {"codigo": "901234", "nombre": "Oli",    "porcentaje": 3.83},
    {"codigo": "567890", "nombre": "James",  "porcentaje": 5.19},
]

# ------------------- Fondo 2: Pestillo Capital -------------------
FONDO2_TOTAL = 80000.0
DIVIDENDO_70 = 56000.0  # 70% para reparto proporcional
DIVIDENDO_30 = 24000.0  # 30% para reparto Kush

# Aportaciones originales (BTC)
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

# Total BTC para calcular participación
total_btc_f2 = sum(aportes_f2.values())

# Nombres para reparto Kush (dividendo especial)
kush_names = {"javi", "pata", "rafa"}
kush_fixed_div = DIVIDENDO_30 / len(kush_names)  # Reparto igual para ellos tres

# Construimos lista inversores_f2 con participaciones y dividendos
inversores_f2 = []
for nombre, btc in aportes_f2.items():
    participacion = (btc / total_btc_f2) * 100
    div_normal = (participacion / 100) * DIVIDENDO_70
    if nombre.lower() in kush_names:
        div_kush = kush_fixed_div
    else:
        div_kush = 0.0
    total_div = div_normal + div_kush
    inversores_f2.append({
        "nombre": nombre,
        "participacion": participacion,
        "div_normal": round(div_normal, 2),
        "div_kush": round(div_kush, 2),
        "total": round(total_div, 2)
    })

# ------------------- Histórico Fondo 2 -------------------
HISTORICO_FILE = "historico_fondo2.csv"
INVERSION_INICIAL = 6000.0
FECHA_REFERENCIA = datetime(2021, 1, 1)

def cargar_historico():
    if not os.path.isfile(HISTORICO_FILE):
        # Crear archivo con valor inicial si no existe
        df = pd.DataFrame({
            "fecha": [FECHA_REFERENCIA.strftime("%Y-%m-%d")],
            "valor": [INVERSION_INICIAL]
        })
        df.to_csv(HISTORICO_FILE, index=False)
        return df
    else:
        return pd.read_csv(HISTORICO_FILE, parse_dates=["fecha"])

def agregar_valor_actual(valor):
    df = cargar_historico()
    hoy = datetime.now().strftime("%Y-%m-%d")
    if hoy in df['fecha'].dt.strftime("%Y-%m-%d").values:
        return False  # Ya existe valor para hoy
    nuevo = pd.DataFrame({"fecha": [hoy], "valor": [valor]})
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(HISTORICO_FILE, index=False)
    return True

def generar_grafico():
    df = cargar_historico()
    df = df.sort_values("fecha")
    df["pnl"] = df["valor"] - INVERSION_INICIAL  # Ganancia o pérdida respecto a inversión inicial

    plt.figure(figsize=(10,5))
    plt.axhline(0, color='gray', linestyle='--')
    plt.plot(df["fecha"], df["pnl"], marker='o', color='green')
    plt.fill_between(df["fecha"], df["pnl"], 0, where=(df["pnl"] >= 0), facecolor='green', alpha=0.3)
    plt.fill_between(df["fecha"], df["pnl"], 0, where=(df["pnl"] < 0), facecolor='red', alpha=0.3)
    plt.title("P&L Histórico - Pestillo Capital")
    plt.xlabel("Fecha")
    plt.ylabel("Ganancia/Pérdida (USD)")
    plt.grid(True)
    plt.tight_layout()

    img_path = "grafico_fondo2.png"
    plt.savefig(img_path)
    plt.close()
    return img_path

# ------------------- Comandos de tablas -------------------

@bot.message_handler(commands=['tabla1'])
def enviar_tabla1(message):
    tabla = "📋 *Fondo de Recuperación*\n\n"
    tabla += "Código   Nombre      %       Monto USD\n"
    tabla += "----------------------------------------\n"
    for inv in sorted(inversores_f1, key=lambda x: x['porcentaje'], reverse=True):
        monto = round((inv["porcentaje"] / 100) * FONDO1_TOTAL, 2)
        tabla += f"{inv['codigo']:<8} {inv['nombre']:<10} {inv['porcentaje']:>6.2f}%  ${monto:>10,.2f}\n"
    tabla += "----------------------------------------\n"
    tabla += f"{'Total':<20} {100.00:>6.2f}%  ${FONDO1_TOTAL:>10,.2f}\n"
    bot.send_message(message.chat.id, f"```\n{tabla}```", parse_mode='Markdown')

@bot.message_handler(commands=['tabla2'])
def enviar_tabla2(message):
    tabla = "📋 *Pestillo Capital*\n\n"
    tabla += "Nombre     %        Dividendo $    Div. Kush $   Total $\n"
    tabla += "----------------------------------------------------------\n"
    for inv in sorted(inversores_f2, key=lambda x: x['participacion'], reverse=True):
        tabla += f"{inv['nombre']:<10} {inv['participacion']:>6.2f}%     ${inv['div_normal']:>10,.2f}   ${inv['div_kush']:>9,.2f}   ${inv['total']:>10,.2f}\n"
    tabla += "----------------------------------------------------------\n"
    tabla += f"{'TOTAL':<10} {100.00:>6.2f}%     ${DIVIDENDO_70:>10,.2f}   ${DIVIDENDO_30:>9,.2f}   ${FONDO2_TOTAL:>10,.2f}"
    bot.send_message(message.chat.id, f"```\n{tabla}```", parse_mode='Markdown')

# ------------------- Nuevo comando: graficofondo2 -------------------

@bot.message_handler(commands=['graficofondo2'])
def enviar_grafico(message):
    img_path = generar_grafico()
    with open(img_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="📈 P&L Histórico de Pestillo Capital desde 01-01-2021")

# ------------------- Nuevo comando: actualizarvalor -------------------

@bot.message_handler(commands=['actualizarvalor'])
def actualizar_valor(message):
    try:
        partes = message.text.split()
        if len(partes) != 2:
            raise ValueError("Formato incorrecto")
        valor = float(partes[1])
        exito = agregar_valor_actual(valor)
        if exito:
            bot.reply_to(message, f"✅ Valor ${valor:.2f} registrado para hoy.")
        else:
            bot.reply_to(message, "⚠️ Ya hay un valor registrado para hoy.")
    except Exception as e:
        bot.reply_to(message, "❌ Uso correcto: /actualizarvalor <valor> (ejemplo: /actualizarvalor 75000)")

# ------------------- Consulta individual -------------------

@bot.message_handler(func=lambda message: True)
def responder(message):
    nombre_input = message.text.strip().lower()
    total_general = 0.0
    respuesta = ""



