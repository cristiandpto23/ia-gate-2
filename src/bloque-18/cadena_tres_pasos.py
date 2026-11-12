from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from termcolor import cprint


def construir_cadena(modelo):
    """Construye un chain de tres pasos encadenados con LCEL
    
    Paso 1: Extraer 3 ideas principales de un texto.
    Paso 2: Reescribir las ideas en lenguaje simple sin tecnicismos.
    Paso 3: Formatear en una lista de viñetas markdown.
    """
    
    # 1 definición de las 3 plantillas
    plantilla_extraccion = PromptTemplate.from_template(
        "Lee el siguiente texto y extrae exactamente sus 3 ideas principales, "
        "una por línea, sin explicaciones adicionales:\n\n{texto}"
    )
    
    plantilla_simplificacion = PromptTemplate.from_template(
        "Reescribe estas ideas en un lenguaje sencillo, claro y sin jerga técnica, "
        "para alguien que no es especialista:\\n\\n{ideas}"
    )
    
    plantilla_formato = PromptTemplate.from_template(
        "Convierte el siguiente texto en una lista de viñetas Markdown (máximo 3 puntos), "
        "sin títulos ni introducciones:\n\n{texto_simple}"
    )
    
    # 2. Encadenamiento secuencial con el operador
    
    cadena = (
        plantilla_extraccion
        | modelo
        | StrOutputParser()
        | (lambda ideas: { "ideas": ideas })
        | plantilla_simplificacion
        | modelo 
        | StrOutputParser()
        | (lambda texto_simple: {"texto_simple": texto_simple })
        | plantilla_formato
        | modelo
        | StrOutputParser()
    )
    
    return cadena
 
 
if __name__ == "__main__":
    load_dotenv()
    
    # instancia del modelo
    modelo_gemini = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        )
    
    cadena = construir_cadena(modelo_gemini)
 
    texto_ejemplo = (
        "La tokenización es el proceso fundamental mediante el cual los modelos "
        "de lenguaje transforman secuencias de caracteres continuas en unidades "
        "discretas llamadas tokens. Estos tokens no siempre equivalen a palabras completas, "
        "sino que frecuentemente representan fragmentos sub-léxicos que optimizan el "
        "vocabulario del modelo. Durante el preentrenamiento, las arquitecturas tipo "
        "Transformer asignan embeddings vectoriales a cada uno de estos identificadores "
        "numéricos para calcular pesos de autoatención probabilística."
    )
 
    cprint("=== EJECUTANDO CADENA DE 3 PASOS ===", color="green")
    resultado = cadena.invoke({"texto": texto_ejemplo})
    print(resultado)
