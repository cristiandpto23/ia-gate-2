import sys
from pathlib import Path

# aseguramos la ruta local para imports limpios
sys.path.insert(0, str(Path(__file__).parent))

from langchain_core.runnables import RunnableLambda
from resiliencia import construir_cadena_resiliente


def test_fallback_se_activa_cuando_falla_cadena_principal():
  # 1. Creamos una cadena principal que falla a propósito con una excepción
  def simular_caida_api(x):
    raise ConnectionError("503 Service Unavailable: Error de conexión con Gemini")

  cadena_principal_rota = RunnableLambda(simular_caida_api)

  # 2. creamos un fallback que devuelva un mensaje de respaldo
  fallback_auxiliar = RunnableLambda(
      lambda x: "Respuesta de contingencia exitosa"
  )

  # 3. construimos la cadena resiliente
  cadena_segura = construir_cadena_resiliente(
      cadena_principal=cadena_principal_rota, fallback=fallback_auxiliar
  )

  # 4. invocamos: no debe lanzar ConnectionError, debe salvarlo el fallback
  resultado = cadena_segura.invoke({"pregunta": "Hola"})

  assert resultado == "Respuesta de contingencia exitosa"

def test_cadena_principal_se_usa_cuando_no_hay_error():
  # 1. camino feliz: la cadena principal funciona normalmente
  cadena_principal_ok = RunnableLambda(
      lambda x: "Respuesta normal del modelo principal"
  )

  # 2. el fallback existe, pero no debería activarse
  fallback_auxiliar = RunnableLambda(lambda x: "Respuesta de contingencia")

  cadena_segura = construir_cadena_resiliente(
      cadena_principal=cadena_principal_ok, fallback=fallback_auxiliar
  )

  resultado = cadena_segura.invoke({"pregunta": "Hola"})

  # comprobamos que se respetó la salida principal y no el fallback
  assert resultado == "Respuesta normal del modelo principal"

def test_fallback_por_defecto_cuando_no_se_pasa_uno():
  # probamos que si fallback=None, usa el mensaje estático por defecto
  def simular_error(x):
    raise TimeoutError("Timeout en la API")

  cadena_rota = RunnableLambda(simular_error)
  cadena_segura = construir_cadena_resiliente(cadena_principal=cadena_rota)

  resultado = cadena_segura.invoke({"pregunta": "Hola"})

  assert (
      resultado
      == "El servicio no está disponible en este momento. Por favor, intenta"
      " más tarde."
  )