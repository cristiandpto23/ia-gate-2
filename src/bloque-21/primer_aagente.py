import os

from dotenv import load_dotenv

# AgentExecutor y create_tool_calling_agent desde langchain-classic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# prompts para agentes
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# herramientas y llm
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. definición de herramientas - @tool

BASE_DOCUMENTACION = {
    "reintentos": "El cliente reintenta hasta 3 veces antes de fallar",
    "costos": "El modelo flash cuesta 0.0001 dólares por cada mil tokens.",
}

@tool
def buscar_en_documentacion(consulta: str) -> str:
    """Busca información técnica en la documentación interna.
    Útil para saber sobre reintentos, políticas del cliente o costos."""
    consulta_limpia = consulta.lower()
    for clave, valor in BASE_DOCUMENTACION.items():
        if clave in consulta_limpia:
            return valor
        return "No se encontró información sobre ese tema en la documentación."
    
@tool
def calcular(expresion: str) -> str:
    """Evalúa operaciones matemáticas básicas como sumas, restas, multiplicaciones y divisiones.
    Usa solo números y operadores estándar: +, -, *, (, )."""
    # filtro básicos de seguridad
    caracteres_permitidos = "0123456789+-*/(). "
    if not all(c in caracteres_permitidos for c in expresion):
        return "Error: la expresión contiene caracteres no permitidos."
    try:
        resultado = eval(expresion)
        return str(resultado)
    except Exception as e:
        return f"Error al calcular: {e}"
    
# 2. ensamblaje del agente
def crear_agente(modelo, herramientas):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente técnico útil y conciso. Tienes herramientas a tu disposición; úsalas cuando sea necesario."),
        ("human", "{input}"),
        # el bloc de notas donde el agente guarda qué pensó y qué observó en cada paso
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    agente = create_tool_calling_agent(
        llm=modelo,
        tools=herramientas,
        prompt=prompt
    )
    
    # AgentExecutor ejecuta el ciclo de razonamiento (ReAct)
    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True, # para ver en consola qué herramienta decide invocar
        return_intermediate_steps=True
    )
    
# 3. ejecucion 

if __name__ == "__main__":
    load_dotenv()
    api_key= os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: falta GEMINI_API_KEY")
        exit(1)
        
    # inicializamos el modelo
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=api_key,
        temperature=0
    )
    
    herramientas = [buscar_en_documentacion, calcular]
    ejecutor = crear_agente(llm, herramientas)
    
    # 4 pruebas para observar el comportamiento dinámico del agente
    consultas = [
        "¿Cuánto es 340 más 215?",
        "¿Cuántas veces reintenta el cliente ante un error?",
        "¿Cuántas veces reintenta el cliente, y cuánto sería eso multiplicado por 2?",
        "¿Qué significa la sigla API en informática?",
    ]
    
    for consulta in consultas:
        print("\n" + "=" * 60)
        print(f"CONSULTA: {consulta}")
        print("=" * 60)
        respuesta = ejecutor.invoke({"input": consulta})
        
        # extraemos el texto limpio si viene con estructura de bloques de gemini
        salida = respuesta["output"]
        if isinstance(salida, list) and len(salida) > 0 and isinstance(salida[0], dict):
            texto_limpio = salida[0].get("text", salida)
        else:
            texto_limpio = salida
        print(f"\nRespuesta final:\n{texto_limpio}")
