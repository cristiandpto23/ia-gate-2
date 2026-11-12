from unittest.mock import MagicMock

from cadena_tres_pasos import construir_cadena
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda


def test_cadena_tres_pasos_ejecuta_correctamente():
    # 1. definimos las 3 respuestas simuladas en orden
    respuestas = [
        AIMessage(content="Punto 1\nPunto 2\nPunto 3"), 
        AIMessage(content="Texto simplificado y claro"), 
        AIMessage(content="* Viñeta 1\n* Viñeta 2\n* Viñeta 3"),
    ]
    
    # Usamos un mock para rastrear las llamadas
    mock_tracker = MagicMock()
    
    def responder_falso(prompt_input): 
        mock_tracker(prompt_input)
        return respuestas.pop(0)

    # 2. envolvemos la función con RunnableLambda para que LangChain acepte el operador |
    modelo_mock = RunnableLambda(responder_falso)
    
    # 3. construimos y ejecutamos la cadena 
    cadena = construir_cadena(modelo_mock)
    resultado = cadena.invoke({"texto": "Texto de prueba de entrada"})
    
    # 4. verificaciones
    assert mock_tracker.call_count == 3
    assert respuestas == []
    assert resultado == "* Viñeta 1\n* Viñeta 2\n* Viñeta 3"