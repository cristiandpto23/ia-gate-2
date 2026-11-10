import json
import os
import re
import time
from collections.abc import Callable
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_INSTRUCTION_DEFAULT = (
    "Responde únicamente con un objeto JSON válido, sin texto adicional "
    "y sin usar bloques de markdown. El JSON debe tener exactamente estas "
    "claves: 'categoria' (string), 'confianza' (número entre 0 y 1), 'respuesta' (string). "
    "respuesta: (string) en solo 1 a 5 palabras, sin saltos de línea ni comillas dobles."
)


def armar_peticion(
    pregunta: str,
    system_instruction: str | None = None,
    modelo: str = "gemini-3.5-flash-lite",
    response_schema: dict | None = None,
):
    pregunta = pregunta.strip()
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")

    if not GEMINI_API_KEY:
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    if system_instruction is None:
        system_instruction = SYSTEM_INSTRUCTION_DEFAULT

    # Seguridad extra si alguien pasa modelo=None
    if not modelo:
        modelo = "gemini-2.5-flash"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"

    body = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": pregunta}]}],
    }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, body

def enviar_peticion(url: str, cuerpo: dict[str, Any]) -> dict:
    headers = {"Content-Type": "application/json"}
    try:
        respuesta = requests.post(url, json=cuerpo, headers=headers, timeout=15)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")

    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")

    respuesta.raise_for_status()
    return respuesta.json()


def extraer_texto(datos: dict) -> str:
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no contiene texto generado en la estructura esperada.")


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera_segundos)
