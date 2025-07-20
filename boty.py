import time
import hmac
import hashlib
import requests
import os

# Puedes definir aquí directamente si no tienes .env
MEXC_API_KEY = "mx0vgleAS50BKM96Uu"
MEXC_SECRET_KEY = "8c6b74ceec1543158b067de52b0a1084"
BASE_URL = 'https://api.mexc.com'

def test_mexc_account():
    timestamp = int(time.time() * 1000)
    query_string = f'timestamp={timestamp}'
    signature = hmac.new(MEXC_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    headers = {
        'X-MEXC-APIKEY': MEXC_API_KEY
    }

    url = f"{BASE_URL}/api/v3/account?{query_string}&signature={signature}"
    response = requests.get(url, headers=headers)

    print("Código de respuesta:", response.status_code)
    print("Respuesta JSON:")
    print(response.json())

test_mexc_account()
