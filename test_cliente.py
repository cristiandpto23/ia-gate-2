from unittest.mock import Mock, patch
import pytest

from cliente_api import enviar_peticion

import cliente
from cliente import con_reintento, consultar_modelo, registrar_costo


# ===================================================================== 
# Fixture de aislamiento
# ===================================================================== 
@pytest.fixture(autouse=True)
def reiniciar_costo_sesion():
    cliente.costo_total_sesion = 0.0
    yield
    cliente.costo_total_sesion = 0.0


# ===================================================================== 
# 1. Pruebas para enviar_peticion (cliente_api.py) 
# =====================================================================

def test_enviar_peticion_credencial_invalida():
    # verifica que status 401 lance ValueError de inmediato
    respuesta_falsa = Mock(status_code=401)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion({"pregunta": "test"})

def test_enviar_peticion_limite_de_uso():
    # verifica que status 429 lance TimeoutError
    respuesta_falsa = Mock(status_code=429)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})
            
def text_enviar_peticion_error_servidor():
    # status 503 debe lanzar TimeoutError para reintentos
    respuesta_falsa = Mock(status_code=503)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})

def test_enviar_peticion_exito():
    # verifica que una respuesta 200 retorne el JSON tal cual
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}

    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion({"pregunta": "test"})

    assert resultado == {"texto": "respuesta simulada"}
    
# ===================================================================== 
# 2. Pruebas para con_reintento (cliente.py) 
# =====================================================================

def test_con_reintento_exito_en_primer_intento():
    # verifica que función tiene éxito al inicio, no duerme ni reintenta
    funcion_exitosa = Mock(return_value="respuesta directa")
    with patch("cliente.time.sleep") as mock_sleep:
        resultado = con_reintento(funcion_exitosa, intentos=3)
    assert resultado == "respuesta directa"
    assert funcion_exitosa.call_count == 1
    mock_sleep.assert_not_called()
    
def test_con_reintento_recupera_en_segundo_intento():
    # verifica falla con TimeoutError en primer intento y éxito en segundo
    funcion_recuperable = Mock(side_effect=[TimeoutError("Falla temporal de red"), "éxito en intento 2"])
    with patch("cliente.time.sleep") as mock_sleep:
        resultado = con_reintento(funcion_recuperable, intentos=3)
    assert resultado == "éxito en intento 2"
    assert funcion_recuperable.call_count == 2
    assert mock_sleep.called

def test_con_reintento_agota_intentos():
    # verifica que propague TimeoutError tras agotar y llame a sleep
    funcion_que_falla = Mock(side_effect=TimeoutError("Error transitorio"))
    
    # mockeamos time.sleep en cliente.py para que el test no espere segundos reales
    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(TimeoutError):
            con_reintento(funcion_que_falla, intentos=3)
            
    assert funcion_que_falla.call_count == 3
    assert mock_sleep.call_count == 2
    
def test_con_reintento_no_reintenta_value_error(): 
    # verifica que un error no transitorio (ValueError) falle en el 1er intento sin sleep.
    funcion_con_error_fatal = Mock(side_effect=ValueError("Credencial inválida")) 
    with patch("cliente.time.sleep") as mock_sleep: 
        with pytest.raises(ValueError): 
            con_reintento(funcion_con_error_fatal, intentos=3) 
        
    assert funcion_con_error_fatal.call_count == 1 
    mock_sleep.assert_not_called()
    
    
# ===================================================================== 
# 3. Pruebas para registrar_costo (cliente.py) 
# ===================================================================== 
def test_registrar_costo_acumula():
    # Verifica el cálculo de costo por tokens y su acumulación en la sesión.
    # Reiniciamos el acumulador global de cliente.py para aislar la prueba 
    cliente.costo_total_sesion = 0.0 
    
    respuesta_simulada = {
        "usageMetadata": { 
            "promptTokenCount": 100, 
            "candidatesTokenCount": 50, 
            "totalTokenCount": 150, 
        } 
    } 
    
    costo_llamada = registrar_costo(respuesta_simulada) 
    assert costo_llamada > 0 
    assert cliente.costo_total_sesion == costo_llamada 
    
# ===================================================================== 
# 4. Pruebas para consultar_modelo (cliente.py) 
# ===================================================================== 
def test_consultar_modelo_convierte_error(): 
    #Verifica que un TimeoutError agotado se convierta en RuntimeError para el usuario.
    with patch("cliente.enviar_peticion", side_effect=TimeoutError("Servicio caído")):
        with patch("cliente.time.sleep"): # Evita demoras de backoff 
            with pytest.raises(RuntimeError): 
                consultar_modelo("¿Cuál es la capital de Chile?")