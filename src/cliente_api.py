import os
from typing import Any, Literal

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TipoModelo = Literal["gemini-3.5-flash-lite", "gemini-3.8-flash"] 
modelo: TipoModelo = "gemini-3.5-flash-lite"

url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"

headers = {"Content-Type": "application/json"}

"""
SYSTEM_INSTRUCTION_DEFAULT = (
    "Responde únicamente con un objeto JSON válido, sin texto adicional "
    "y sin usar bloques de markdown. El JSON debe tener exactamente estas "
    "claves: 'categoria' (string), 'confianza' (número entre 0 y 1), 'respuesta' (string). "
    "respuesta: (string) en solo 1 a 5 palabras, sin saltos de línea ni comillas dobles."
)
"""

SYSTEM_INSTRUCTION_DEFAULT = (
    "Eres un asistente técnico útil y ultra conciso. "
    "Tu salida debe ser exclusivamente texto plano crudo (raw plain text). "
    "Prohibido usar cualquier símbolo de formato Markdown: no uses asteriscos (** o *),"
    "ni almohadillas (#), ni guiones (-), ni comillas (\"), ni acentos (`). "
    "Tu respuesta debe tener entre 1 y 5 palabras en una sola línea continua."
)

def armar_peticion(
    pregunta: str,
    system_instruction: str | None = None,
    response_schema: dict | None = None,
) -> dict:
    pregunta = pregunta.strip()
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")

    if not GEMINI_API_KEY:
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")

    if system_instruction is None:
        system_instruction = SYSTEM_INSTRUCTION_DEFAULT

    body = {
        "contents": [{"parts": [{"text": pregunta}]}],
    }
    
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return body

def enviar_peticion(cuerpo: dict[str, Any]) -> dict:
    try:
        respuesta = requests.post(url, json=cuerpo, headers=headers, timeout=10)
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




