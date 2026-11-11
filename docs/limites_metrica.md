# Límites de la métrica de evaluación léxica

## Qué mide

Mide la coincidencia léxica entre una respuesta generada y una referencia esperada tras ser normalizadas con `procesar_texto` (minúsculas y remoción de puntuación). 

En el pipeline base (`pipeline_texto.py`), `calcular_coincidencia` opera sobre conjuntos (`set`), devolviendo una única proporción de solapamiento de vocabulario único sin considerar repeticiones ni orden. 

Por su parte, las métricas compuestas de precisión, cobertura y F1-score reportadas en este análisis se calcularon en el evaluador de lote (`generar_dataset.py` / `calcular_metricas`), el cual cuantifica repeticiones de tokens mediante intersección de frecuencias (`Counter &amp; Counter`) y genera el archivo `resultados_metricas.json`.

## Modos de falla conocidos

A partir de la auditoría sobre `resultados_metricas.json`, se evidenciaron los siguientes límites en los 10 casos revisados:

- **Sensibilidad a acentos y tildes:** El pipeline no remueve tildes, por lo que respuestas factualmente perfectas como `"Oxigeno"` o `"Jupiter"` obtienen `F1 = 0.0` frente a `"oxígeno"` o `"Júpiter"`.

- **Representación numérica (palabras vs. dígitos):** Respuestas como `"Mil novecientos noventa y uno"` o `"Trescientos sesenta y seis dias"` reciben `F1 = 0.0` al compararse con `"1991"` o `"366"`, a pesar de ser exactas en contenido.

- **Castigo a respuestas concisas:** En preguntas como "¿Quién pintó la Mona Lisa?", responder `"Leonardo da Vinci"` obtiene solo `F1 = 0.5` debido a que la referencia contiene texto de relleno ("La Mona Lisa fue pintada por...").

- **Falsos positivos por palabras comunes:** Respuestas erróneas como `"El rio Nilo"` obtienen F1 positivo (0.1538) gracias a artículos compartidos ("el"), ocultando una equivocación factual directa frente al Amazonas.

## Muestra revisada

Muestra balanceada de 10 casos extraídos de `resultados_metricas.json` y auditados en `revision_manual.py`: los 5 con menor F1 (cuatro casos con F1 = 0.0 y el caso del río Nilo con F1 = 0.1538) y los 5 con mayor F1 (valores entre 0.5 y 1.0).

## Recomendación de uso para el pipeline

Dado que `calcular_coincidencia` en `pipeline_texto.py` opera convirtiendo las listas de tokens a conjuntos (`set`), mide únicamente la intersección de palabras únicas compartidas sin considerar frecuencias, estructura sintáctica ni significado factual:

- Usar las métricas de solapamiento del pipeline y el F1 derivado en `generar_dataset.py` exclusivamente para monitoreo automatizado de regresiones de vocabulario y variaciones de texto en lotes masivos.

- No utilizar la métrica del pipeline como criterio de verdad o aceptación en producción ante respuestas que contengan fechas, números, nombres propios o negaciones.
- Para validación de precisión fáctica, complementar el pipeline con auditorías humanas estructuradas o evaluación semántica mediante embeddings y modelos de lenguaje evaluadores.
