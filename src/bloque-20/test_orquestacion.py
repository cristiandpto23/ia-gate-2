import sys
from pathlib import Path
from unittest.mock import MagicMock

# ajuste de ruta para imports locales
sys.path.insert(0, str(Path(__file__).parent))

from enrutamiento import (
  construir_cadena_con_enrutamiento,
  construir_cadena_queja_segura,
  construir_paso_clasificacion,
  procesar_mensaje_seguro,
)
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda


# 1. verificación de clasificación y normalización
def test_clasificacion_normaliza_antes_de_comparar():
  modelo_falso = RunnableLambda(lambda x: AIMessage(content="   Queja \n"))
  resultado = construir_paso_clasificacion(modelo_falso).invoke(
      {"mensaje": "algo salió mal"}
  )
  assert resultado == "queja"

# 2. verificación de enrutamiento a rama queja
def test_enrutamiento_va_a_cadena_queja():
  clasificacion_falsa = MagicMock(return_value="queja")
  cadena_queja_falsa = MagicMock(return_value="respuesta de queja")

  cadena = construir_cadena_con_enrutamiento(
      paso_clasificacion=clasificacion_falsa,
      cadena_queja=cadena_queja_falsa,
  )
  resultado = cadena.invoke({"mensaje": "esto no funciona nunca"})

  assert cadena_queja_falsa.called
  assert resultado == "respuesta de queja"

# 3. verificación de enrutamiento a ruta por defecto ante categoría desconocida
def test_enrutamiento_usa_default_ante_categoria_desconocida():
  clasificacion_falsa = MagicMock(return_value="categoria_inventada")
  cadena_pregunta_falsa = MagicMock(return_value="respuesta por defecto")

  cadena = construir_cadena_con_enrutamiento(
      paso_clasificacion=clasificacion_falsa,
      cadena_pregunta=cadena_pregunta_falsa,
  )
  resultado = cadena.invoke({"mensaje": "mensaje ambiguo"})

  assert cadena_pregunta_falsa.called
  assert resultado == "respuesta por defecto"

# 4. verificación de fallback en ruta de quejas
def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():

  def fallar_a_proposito(x):
    raise ConnectionError("simulado")

  cadena_queja_falsa = RunnableLambda(fallar_a_proposito)
  cadena_queja_segura = construir_cadena_queja_segura(cadena_queja_falsa)

  resultado = cadena_queja_segura.invoke({"mensaje": "esto no funciona"})

  assert "equipo" in resultado.lower()

# 5. verificación de protección global (falla antes de la bifurcación)
def test_procesar_mensaje_seguro_no_propaga_excepciones():

  def fallar_clasificacion(x):
    raise ConnectionError("simulado")

  paso_roto = RunnableLambda(fallar_clasificacion)
  cadena_falsa = construir_cadena_con_enrutamiento(
      paso_clasificacion=paso_roto,
  )

  resultado = procesar_mensaje_seguro(cadena_falsa, "mensaje de prueba")

  assert "no pudimos procesar" in resultado.lower()
