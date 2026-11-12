import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI


def construir_cadena_enrutamiento(modelo):
    """ Construye nu flujo con enrutamiento condicional (bifurcación)
    
    usando RunnableBranch y RunnablePassthrough.assign.
    """
    # 1. paso clasificador: detectar la categoría del mensaje
    plantilla_clasificador = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de un usuario exactamente en una de estas "
        "tres categorías: 'pregunta', 'queja' o 'sugerencia'.\n"
        "Responde ÚNICAMENTE con la palabra de la categoría en minúsculas, sin puntuación ni texto adicional.\n\n"
        "Mensaje: {mensaje}"
    )
    
    # cadena que toma {"mensaje": "..."} y devuelve solo el string con la categoría limpia
    cadena_clasificacion = (
        plantilla_clasificador
        | modelo
        | StrOutputParser()
        | (lambda x: x.strip().lower())
    )
    
    # 2. definir las 3 ramas especializadas de respuesta
    # rama A. pregunta técnica (directa, concisa y precisa)
    prompt_pregunta = PromptTemplate.from_template(
        "Eres un asistente técnico. Responde de manera clara, directa y concisa a la siguiente pregunta:\n\n"
        "{mensaje}"
    )
    cadena_pregunta = prompt_pregunta | modelo | StrOutputParser()
    
    # rama B. queja. (empática, reconociendo el problema antes de proponer solución)
    prompt_queja = PromptTemplate.from_template(
        "Eres un especialista en atención al cliente. Un usuario presenta la siguiente queja."
        "Responde con empatía, reconociendo el inconveniente con profesionalismo y ofreciendo los primeros pasos para resolverlo:\n\n"
        "{mensaje}"
    )
    cadena_queja = prompt_queja | modelo | StrOutputParser()
    
    # rama C. sugerencia. (agradecida y explicando el valor del feedback)
    prompt_sugerencia = PromptTemplate.from_template(
        "Eres parte del equipo de producto. Un usuario envía la siguiente sugerencia. "
        "Agradece su aporte y explica cómo el equipo evalúa estas ideas para futuras mejoras:\n\n"
        "{mensaje}"
    )
    cadena_sugerencia = prompt_sugerencia | modelo | StrOutputParser()
    
    # 3. la bifurcación (RunnableBranch)
    # evalúa condiciones (lambda x: condicion, rama_a_ejecutar)    
    # la última rama sin tupla actúa como el 'else' por defecto
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta, #ruta por defecto
    )

    # 4. unir todo en la cadena completa
    # RunnablePassthrough.assign toma el input inicial {"mensaje": "..."}
    # ejecuta cadena_clasificacion y agrega la clave "categoria" sin perder "mensaje"
    cadena_completa = (
        RunnablePassthrough.assign(categoria=cadena_clasificacion)
        | bifurcacion
    )
    
    return cadena_completa
    
# ------------------
# ejecución manual

if __name__ == "__main__":
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY") 
    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        google_api_key=api_key
    )
    
    cadena = construir_cadena_enrutamiento(modelo)
    
    # mensajes de prueba para disparar las distintas ramas
    ejemplos = [
        "¿Cómo puedo cambiar la contraseña de mi cuenta desde la configuración?",
        "Llevo dos semanas esperando mi reembolso y nadie responde. ¡Es inaceptable!",
        "Sería fantástico si pudieran agregar un modo oscuro para trabajar de noche.",
    ]
    
    for mensaje_usuario in ejemplos:
        print(f"\n📥 Entrada: {mensaje_usuario}")
        respuesta = cadena.invoke({"mensaje": mensaje_usuario})
        print(f"📥 Respuesta:\n{respuesta}\n" + "-" * 50)