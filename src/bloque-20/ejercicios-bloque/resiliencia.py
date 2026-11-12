import logging
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuramos logging para registrar cuando se active un fallback 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

def construir_cadena_resiliente(cadena_principal, fallback=None):
    """
    Construye una cadena protegida con fallbacks.
    Si la cadena principal falla, se ejecuta automáticamente el fallback.
    """
    if fallback is None:
        # fallback por defecto: respuesta estática y segura 
        fallback = RunnableLambda(
            lambda x: "El servicio no está disponible en este momento. Por favor, intenta más tarde."
        ) 
        
    # asociamos el fallback a la cadena principal 
    cadena_segura = cadena_principal.with_fallbacks([fallback])
    return cadena_segura
    
# ----------------------
# ejecución manual
if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: No se encontró la API Key.")
        exit(1)

    prompt = PromptTemplate.from_template("Responde brevemente a: {pregunta}")
    
    # 1. Cadena principal con modelo primario
    modelo_principal = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=api_key,
        temperature=0
    )
    cadena_principal = prompt | modelo_principal | StrOutputParser()

    # 2. Cadena de fallback con modelo secundario o más ligero
    modelo_secundario = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=api_key,
        temperature=0
    )
    cadena_fallback = prompt | modelo_secundario | StrOutputParser()

    # 3. Ensamblamos la cadena tolerante a fallos
    cadena_final = construir_cadena_resiliente(
        cadena_principal=cadena_principal,
        fallback=cadena_fallback
    )

    print("Probando cadena resiliente...")
    try:
        respuesta = cadena_final.invoke({"pregunta": "¿Qué es la resiliencia en software?"})
        print(f"\nRespuesta:\n{respuesta}")
    except Exception as e:
        logger.error(f"Error imprevisto en la ejecución: {e}")