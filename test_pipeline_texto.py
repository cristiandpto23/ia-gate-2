from pipeline_texto import procesar_texto


def test_procesar_texto_normaliza_correctamente():
    # verifica que minúsculas, puntuación y espacios queden limpios
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]

def test_procesar_texto_solo_puntuacion():
    # verifica que un texto solo con signos devuelva lista vacía
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []