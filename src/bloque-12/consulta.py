import os

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
)

headers = {"Content-Type": "application/json"}

def enviar_peticion(url, body):
    try:
        respuesta = requests.post(URL, json=body, headers=headers, timeout=10)
    except (requests.RequestException, requests.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")

    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")
    
    if respuesta.status_code == 429:
        segundos = respuesta.headers.get("Retry-After")
        mensaje = f"Límite excedido. Reintentar en {segundos}s." if segundos else "Límite excedido."
        raise TimeoutError(mensaje)

    respuesta.raise_for_status()
    return respuesta.json()

print(enviar_peticion(URL, {"systemInstruction": {"parts": [{"text": "Hola"}]}, "contents": [{"parts": [{"text": "Hola"}]}]}))