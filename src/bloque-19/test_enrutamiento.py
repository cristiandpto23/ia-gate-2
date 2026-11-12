from unittest.mock import MagicMock

from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
)
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda


def test_enrutamiento_va_a_cadena_queja():
    # 1. mockeamos el paso de clasificación para que fuerce la categoría "queja"
    clasificador_mock = RunnableLambda(lambda x: "queja")

    # 2. mockeamos la rama de quejas
    mock_queja = MagicMock()
    mock_queja.return_value = "Respuesta de soporte empática"
    rama_queja = RunnableLambda(mock_queja)

    # 3. construimos la cadena inyectando el clasificador y la rama mockeada
    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador_mock,
        cadena_queja=rama_queja,
    )

    resultado = cadena.invoke({"mensaje": "El servicio se cayó por completo."})

    # 4. verificamos que se ejecutó la rama de quejas y no otra
    assert mock_queja.called
    assert resultado == "Respuesta de soporte empática"

def test_enrutamiento_va_a_cadena_pregunta():
    # 1. forzamos la categoría "pregunta"
    clasificador_mock = RunnableLambda(lambda x: "pregunta")

    # 2. mockeamos la rama de preguntas
    mock_pregunta = MagicMock()
    mock_pregunta.return_value = "Respuesta técnica concisa"
    rama_pregunta = RunnableLambda(mock_pregunta)

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador_mock,
        cadena_pregunta=rama_pregunta,
    )

    resultado = cadena.invoke({"mensaje": "¿Dónde veo mis facturas?"})

    assert mock_pregunta.called
    assert resultado == "Respuesta técnica concisa"

def test_enrutamiento_usa_default_ante_categoria_desconocida():
    # 1. simulamos que el clasificador devuelve una categoría no contemplada
    clasificador_mock = RunnableLambda(lambda x: "categoria_inexistente")

    # 2. mockeamos la rama por defecto (cadena_pregunta actúa como fallback)
    mock_default = MagicMock()
    mock_default.return_value = "Respuesta fallback"
    rama_default = RunnableLambda(mock_default)

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador_mock,
        cadena_pregunta=rama_default,
    )

    resultado = cadena.invoke({"mensaje": "Un mensaje confuso o en otro idioma"})

    # comprobamos que cayó en la ruta por defecto
    assert mock_default.called
    assert resultado == "Respuesta fallback"

def test_clasificacion_normaliza_antes_de_comparar():
    # usamos un RunnableLambda que simula la respuesta sucia del modelo
    # esto evita el error de validación de Pydantic/StrOutputParser
    modelo_mock = RunnableLambda(lambda x: AIMessage(content="   Queja \n"))

    paso_clasificacion = construir_paso_clasificacion(modelo_mock)
    categoria_obtenida = paso_clasificacion.invoke({"mensaje": "No me gusta esto"})

    # debe salir limpia y en minúsculas
    assert categoria_obtenida == "queja"
