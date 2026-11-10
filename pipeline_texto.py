import re

from cliente import consultar_modelo


def limpiar_texto(texto: str) -> str:
    # normaliza texto: minúsculas, sin puntuación y sin espacios repetidos
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def tokenizar(texto_limpio: str) -> list[str]:
    # divide el texto limpio en una lista de palabras individuales.
    return texto_limpio.split()

def procesar_texto(texto: str) -> list[str]: 
    # pipeline completo: limpia y tokeniza el texto en un solo paso
    texto_limpio = limpiar_texto(texto) 
    return tokenizar(texto_limpio)

def calcular_coincidencia(tokens_ref: list[str], tokens_resp: list[str]) -> float: 
    # calcula la proporción de palabras de la referencia presentes en la respuesta 
    if not tokens_ref: 
        return 0.0 
    set_ref = set(tokens_ref) 
    set_resp = set(tokens_resp) 
    comunes = set_ref & set_resp 
    return len(comunes) / len(set_ref)

if __name__ == "__main__": 
    # 3 casos de prueba con respuestas de referencia esperadas 
    casos = [
        {
            "consulta": "¿Qué es Python en una oración corta?", 
            "referencia": "Python es un lenguaje de programación interpretado.", 
        }, 
        { 
            "consulta": "¿De qué color es el cielo durante el día despejado?", 
            "referencia": "El cielo durante el día es de color azul.", 
        }, 
        { 
            "consulta": "¿Cuál es la capital de Chile?", 
            "referencia": "La capital de Chile es Santiago.", 
        }, 
        ] 
    print("=== Comparación: Texto Crudo vs. Texto Procesado ===\n") 
 
    for i, caso in enumerate(casos, start=1): 
        pregunta = caso["consulta"] 
        referencia = caso["referencia"] 
        print(f"--- Caso {i} ---") 
        print(f"Pregunta: {pregunta}") 
        print(f"Referencia: {referencia}") 
        
        # consulta al modelo real usando tu cliente del Bloque 13/14 
        respuesta = consultar_modelo(pregunta) 
        print(f"Respuesta: {respuesta.strip()}") 
        
        # 1. medición sobre texto crudo (split directo, sensible a mayúsculas y puntos) 
        crudo_ref = referencia.split()
        crudo_resp = respuesta.split() 
        pct_crudo = calcular_coincidencia(crudo_ref, crudo_resp) 
        
        # 2. medición sobre texto procesado por el pipeline 
        tokens_ref = procesar_texto(referencia) 
        tokens_resp = procesar_texto(respuesta) 
        pct_proc = calcular_coincidencia(tokens_ref, tokens_resp) 
        print(f"[Caso {i}] Coincidencia texto crudo: {pct_crudo:.1%}") 
        print(f"[Caso {i}] Coincidencia texto procesado: {pct_proc:.1%}\n")