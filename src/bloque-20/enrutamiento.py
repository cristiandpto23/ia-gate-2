import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI


def construir_paso_clasificacion(modelo): 
    # construye el componente clasificador. 
    # toma {"mensaje": "..."} y retorna la categoría en minúsculas y sin espacios.
    
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de un usuario exactamente en una de estas "
        "tres categorías: 'pregunta', 'queja' o 'sugerencia'.\n"
        "Responde ÚNICAMENTE con la palabra de la categoría en minúsculas, sin puntuación ni texto adicional.\n\n"
        "Mensaje: {mensaje}" 
    ) 
    
    return ( 
        plantilla
        | modelo
        | StrOutputParser()
        | (lambda x: x.strip().lower())
    )
    
def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    # construye la cadena con bifurcacion condicional
    # permite inyectar ramas personalizadas 
    # si una rama no se especifica, usa RunnablePassthrough() como valor por defecto
    
    # 1. asignar fallbacks si no se pasaron ramas concretas
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()
    
    # 2. definir la bifurcación condicional
    # si categoria es 'queja' -> cadena_queja
    # si categoria es 'sugerencia' -> cadena_sugerencia
    # cualquier otro caso -> cadena_pregunta
    
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta, # ruta por defecto
    )
    
    # 3. ensamblar con RunnablePassthrough.assign 
    cadena_completa = (
        RunnablePassthrough.assign(categoria=paso_clasificacion)
        | bifurcacion
    )
    
    return cadena_completa


# ----------------------------------------
# piezas de resilencia y manejo de errores


respuesta_generica = RunnableLambda(
    lambda x: (
        "Lamentamos el inconveniente. Un miembro de nuestro equipo te va a"
        " responder pronto."
    )
)

def construir_cadena_queja_segura(cadena_queja):
  """Protege la rama de quejas con un fallback estático razonable."""
  return cadena_queja.with_fallbacks([respuesta_generica])

def procesar_mensaje_seguro(cadena, mensaje):
  """Función de entrada que protege la ejecución global de la cadena.

  Permite inyectar la cadena para poder ser testeada con mocks.
  """
  try:
    return cadena.invoke({"mensaje": mensaje})
  except Exception as error:
    print(f"Error procesando mensaje: {error}")
    return (
        "No pudimos procesar tu mensaje en este momento. Intenta de nuevo más"
        " tarde."
    )


# ----------------
# ejecucion manual

if __name__ == "__main__":
    load_dotenv() 
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key: 
        print("Error: No se encontró la API Key en el entorno.") 
        exit(1) 
    
    modelo = ChatGoogleGenerativeAI( 
        model="gemini-3.5-flash-lite", 
        temperature=0, 
        google_api_key=api_key,
    ) 
    
    # ramas reales especializadas 
    prompt_pregunta = PromptTemplate.from_template(
        "Eres un asistente técnico. Responde conciso a la pregunta:\n\n{mensaje}"
    ) 
    
    prompt_queja = PromptTemplate.from_template( 
        "Eres soporte al cliente. Responde con mucha empatía a la queja:\n\n{mensaje}" 
    )
    
    prompt_sugerencia = PromptTemplate.from_template( 
        "Eres del equipo de producto. Agradece la sugerencia:\n\n{mensaje}"
    ) 
    
    cadena_pregunta = prompt_pregunta | modelo | StrOutputParser() 
    cadena_queja = prompt_queja | modelo | StrOutputParser() 
    cadena_sugerencia = prompt_sugerencia | modelo | StrOutputParser()
    paso_clasificador = construir_paso_clasificacion(modelo)

    cadena_enrutada = construir_cadena_con_enrutamiento( 
        paso_clasificacion=paso_clasificador,
        cadena_queja=cadena_queja, 
        cadena_sugerencia=cadena_sugerencia,
        cadena_pregunta=cadena_pregunta,
    )
    
    mensaje_prueba = "El botón de pago no funciona y se me cobró dos veces." 
    print(f"📥 Probando con: '{mensaje_prueba}'") 
    resultado = cadena_enrutada.invoke({"mensaje": mensaje_prueba})
    print(f"\n📤 Respuesta:\n{resultado}")