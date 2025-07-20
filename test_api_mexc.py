import time
import hmac
import hashlib
import requests

# 🔐 Reemplaza con tus claves reales (o usa variables de entorno)
MEXC_API_KEY = "mx0vglRa0bfuNME6kR"
MEXC_SECRET_KEY = "5534dc44e1b641e69f973f5b08c66369"
BASE_URL = "https://api.mexc.com"

def test_mexc_account():
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(MEXC_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    
    headers = {
        "X-MEXC-APIKEY": MEXC_API_KEY
    }

    url = f"{BASE_URL}/api/v3/account?{query_string}&signature={signature}"
    response = requests.get(url, headers=headers)

    print("Código de respuesta:", response.status_code)
    try:
        print("Respuesta JSON:")
        print(response.json())
    except Exception as e:
        print("Error al interpretar JSON:", e)

# Ejecutar prueba
test_mexc_account()
