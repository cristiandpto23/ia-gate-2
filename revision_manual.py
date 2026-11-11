"""Auditoría cualitativa manual sobre los 10 casos extremos de resultados_metricas.json.""" 

REVISION_MANUAL = [ 
    # ======================================================== 
    # LOS 5 CASOS CON MENOR F1 (Falsos negativos) 
    # ======================================================== 
    { 
        "consulta": "¿En qué año se lanzó Python por primera vez?", 
        "f1": 0.0, 
        "correccion_factual": "si", 
        "completitud": "parcialmente", 
        "contradiccion": "no", 
        "nota": "Falso negativo: F1 da 0.0 porque escribió el año en palabras ('Mil novecientos noventa y uno') en lugar de dígitos ('1991'), pero el año es totalmente correcto.",
    }, 
    { 
        "consulta": "¿Qué gas respiran los seres humanos para vivir?", 
        "f1": 0.0, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "Falso negativo: F1 da 0.0 debido a la tilde ('Oxigeno' vs. 'oxígeno') y concisión extrema, castigando una respuesta que es conceptualmente perfecta.", 
    }, 
    { 
        "consulta": "¿Cuál es el planeta más grande del sistema solar?", 
        "f1": 0.0, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "Falso negativo: F1 da 0.0 por diferencia de acentuación ('Jupiter' vs. 'Júpiter') y omitir la frase de relleno de la referencia.", 
    }, 
    { 
        "consulta": "¿Cuántos días tiene un año bisiesto?", 
        "f1": 0.0, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "Falso negativo: F1 da 0.0 porque expresó la cifra en palabras y sin tilde ('Trescientos sesenta y seis dias' vs. '366 días').", 
    }, 
    { 
        "consulta": "¿Cuál es el río más largo del mundo?", 
        "f1": 0.1538, 
        "correccion_factual": "no", 
        "completitud": "si", 
        "contradiccion": "si", 
        "nota": "Falso positivo: responde 'El rio Nilo' en lugar del Amazonas; la respuesta es factualmente falsa, pero obtiene F1 positivo (0.1538) solo por coincidir en el artículo 'el'.", 
    },
    
    # ======================================================== 
    # LOS 5 CASOS CON MAYOR F1 (Aciertos y límites de longitud) 
    # ======================================================== 
    { 
        "consulta": "¿Qué idioma oficial se habla en Brasil?", 
        "f1": 1.0, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "Acierto perfecto: coincidencia exacta palabra por palabra en la respuesta completa.", 
    }, 
    { 
        "consulta": "¿Cuántos lados tiene un hexágono?", 
        "f1": 0.8, "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "F1 alto legítimo: respondió la cantidad correcta variando solo ligeramente el orden de las palabras.", 
    },
    {
        "consulta": "¿Cuál es el metal más abundante en la corteza terrestre?", 
        "f1": 0.6667, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "F1 alto con paráfrasis: identificó el aluminio correctamente formulando la oración de manera directa.", 
    }, 
    { 
        "consulta": "¿Cuál es la capital de Francia?", 
        "f1": 0.6, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "Correcto: identifica París; el F1 baja a 0.6 solo por diferencia de acento ('Paris' vs 'París') y omitir 'de Francia'.", 
    }, 
    { 
        "consulta": "¿Quién pintó la Mona Lisa?", 
        "f1": 0.5, 
        "correccion_factual": "si", 
        "completitud": "si", 
        "contradiccion": "no", 
        "nota": "Respuesta concisa y exacta ('Leonardo da Vinci'): el F1 se castiga al 0.5 simplemente porque la referencia incluía texto de relleno.", 
    },
] 
    
if __name__ == "__main__":
    print(f"Total de casos auditados manualmente:{len(REVISION_MANUAL)}")
    for i, c in enumerate(REVISION_MANUAL, 1): 
        print(f"[{i}] {c['consulta']} -> F1: {c['f1']} | Factual: {c['correccion_factual']}")