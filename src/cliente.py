import random
import time
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv
from termcolor import cprint

from cliente_api import armar_peticion, enviar_peticion, extraer_texto  # del Gate 1

load_dotenv()

def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)  # Añadir un pequeño jitter para evitar colisiones
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)


# ===================================================================== # 
# Tarifas oficiales para Gemini 3.5 Flash-Lite (por cada 1.000 tokens) 
# ($0.30 y $2.50 por 1M) 
# ===================================================================== 
COSTO_1K_INPUT_GEMINI_35_LITE = 0.30 / 1000 # $0.000300 USD 
COSTO_1K_OUTPUT_GEMINI_35_LITE = 2.50 / 1000 # $0.002500 USD
            
costo_total_sesion = 0.0
 
def registrar_costo(respuesta: dict) -> float:
    global costo_total_sesion
 
    # 1. extraer bloque metadatos de uso
    uso = respuesta.get("usageMetadata", {})
 
    # 2. leer tokens de entrada (prompt) y de salida (candidates)
    prompt_tokens = uso.get("promptTokenCount", 0)
    output_tokens = uso.get("candidatesTokenCount", 0)
    total_tokens = uso.get("totalTokenCount", prompt_tokens + output_tokens)
    
    # 3. calcular costo discriminado
    costo_input = (prompt_tokens / 1000) * COSTO_1K_INPUT_GEMINI_35_LITE
    costo_output = (output_tokens / 1000) * COSTO_1K_OUTPUT_GEMINI_35_LITE
    costo_estimado = costo_input + costo_output
    
    # 4. acumular en la sesion
    costo_total_sesion += costo_estimado
    
    # 5. imprimir resumen de costos
    cprint( f"📊 [USO TOKENS] Entrada: {prompt_tokens} (${costo_input:.6f}) | " f"Salida: {output_tokens} (${costo_output:.6f}) | Total: {total_tokens}", "cyan" )
    cprint( f"💰 [COSTO LLAMADA] ${costo_estimado:.6f} | " f"Acumulado sesión: ${costo_total_sesion:.6f}", "green", attrs=["bold"] )
 
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str | None = None) -> str:
    cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
	respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
	print(respuesta)
	print(f"Costo acumulado de la sesión: ${costo_total_sesion:.5f}")