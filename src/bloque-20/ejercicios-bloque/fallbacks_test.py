from langchain_core.runnables import RunnableLambda


def fallar_a_proposito(x):
    raise Exception("Error simulado de red") 

respuesta_generica = RunnableLambda( 
    lambda x: "Gracias por tu mensaje. Te responderemos pronto."
) 

cadena_rota = RunnableLambda(fallar_a_proposito) 
cadena_segura = cadena_rota.with_fallbacks([respuesta_generica]) 
print(cadena_segura.invoke({"mensaje": "hola"}))