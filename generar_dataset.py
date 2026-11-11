import json
import time
from collections import Counter

from cliente import consultar_modelo
from pipeline_texto import procesar_texto


def contar_coincidencias(tokens_ref: list[str], tokens_resp: list[str]) -> int:
    conteo_ref = Counter(tokens_ref)
    conteo_resp = Counter(tokens_resp)
    interseccion = conteo_ref & conteo_resp
    return sum(interseccion.values())

def calcular_metricas(ref: str, resp: str) -> dict[str, float]:
    tokens_ref = procesar_texto(ref)
    tokens_resp = procesar_texto(resp)

    if not tokens_ref or not tokens_resp:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(tokens_ref, tokens_resp)
    precision = coincidencias / len(tokens_resp)
    cobertura = coincidencias / len(tokens_ref)

    if precision + cobertura == 0.0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * cobertura) / (precision + cobertura)

    return {
        "precision": round(precision, 4),
        "cobertura": round(cobertura, 4),
        "f1": round(f1, 4),
    }

CASOS = [
    {
        "consulta": "¿Cuál es la capital de Francia?",
        "referencia": "La capital de Francia es París.",
    },
    {
        "consulta": "¿En qué año se lanzó Python por primera vez?",
        "referencia": "Python fue lanzado por primera vez en 1991 por Guido van Rossum.",
    },
    {
        "consulta": "¿Qué gas respiran los seres humanos para vivir?",
        "referencia": "Los seres humanos respiran oxígeno para vivir.",
    },
    {
        "consulta": "¿Cuál es el planeta más grande del sistema solar?",
        "referencia": "Júpiter es el planeta más grande del sistema solar.",
    },
    {
        "consulta": "¿Quién escribió Don Quijote de la Mancha?",
        "referencia": "Don Quijote de la Mancha fue escrito por Miguel de Cervantes.",
    },
    {
        "consulta": "¿Cuál es la fórmula química del agua?",
        "referencia": "La fórmula química del agua es H2O.",
    },
    {
        "consulta": "¿Cuántos días tiene un año bisiesto?",
        "referencia": "Un año bisiesto tiene 366 días.",
    },
    {
        "consulta": "¿Qué instrumento mide la temperatura?",
        "referencia": "El instrumento que mide la temperatura es el termómetro.",
    },
    {
        "consulta": "¿Cuál es el océano más grande del mundo?",
        "referencia": "El océano más grande del mundo es el océano Pacífico.",
    },
    {
        "consulta": "¿En qué continente está Egipto?",
        "referencia": "Egipto está ubicado principalmente en el continente africano.",
    },
    {
        "consulta": "¿Qué idioma oficial se habla en Brasil?",
        "referencia": "El idioma oficial de Brasil es el portugués.",
    },
    {
        "consulta": "¿Cuál es el metal más abundante en la corteza terrestre?",
        "referencia": "El aluminio es el metal más abundante en la corteza terrestre.",
    },
    {
        "consulta": "¿Quién pintó la Mona Lisa?",
        "referencia": "La Mona Lisa fue pintada por Leonardo da Vinci.",
    },
    {
        "consulta": "¿Cuántos lados tiene un hexágono?",
        "referencia": "Un hexágono tiene 6 lados.",
    },
    {
        "consulta": "¿Cuál es la moneda oficial de Japón?",
        "referencia": "La moneda oficial de Japón es el yen.",
    },
    {
        "consulta": "¿Qué órgano del cuerpo humano bombea la sangre?",
        "referencia": "El corazón es el órgano encargado de bombear la sangre.",
    },
    {
        "consulta": "¿Cuál es la velocidad de la luz en el vacío aproximadamente?",
        "referencia": "La velocidad de la luz en el vacío es aproximadamente 300000 km por segundo.",
    },
    {
        "consulta": "¿Cuál es el río más largo del mundo?",
        "referencia": "El río más largo del mundo es el río Amazonas.",
    },
    {
        "consulta": "¿Qué elemento tiene el símbolo químico Au?",
        "referencia": "El símbolo químico Au corresponde al oro.",
    },
    {
        "consulta": "¿Cuántos minutos tiene una hora?",
        "referencia": "Una hora tiene exactamente 60 minutos.",
    },
]

if __name__ == "__main__":
    resultados = []
    print("Consultando a Gemini y evaluando 20 casos...")

    for i, item in enumerate(CASOS, 1):
        pregunta = item["consulta"]
        referencia = item["referencia"]

        print(f"[{i}/20] {pregunta}")
        try:
            respuesta = consultar_modelo(pregunta)
        except Exception as e:
            respuesta = f"Error al consultar: {e}"

        metricas = calcular_metricas(referencia, respuesta)

        resultados.append(
            {
                "consulta": pregunta,
                "referencia": referencia,
                "respuesta": respuesta.strip(),
                "precision": metricas["precision"],
                "cobertura": metricas["cobertura"],
                "f1": metricas["f1"],
            }
        )
        time.sleep(1)  # pausa breve

    with open("resultados_metricas.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print("\n¡Listo! Se generó resultados_metricas.json con éxito.")