from cliente_api import armar_peticion, con_reintento, enviar_peticion, extraer_texto


def consultar_modelo(pregunta: str, system_instruction: str | None = None) -> str:
    url, cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(url, cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")

    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
        print(respuesta)
    except ValueError as error:
        print(f"Error de configuración: {error}")
    except RuntimeError as error:
        print(f"Error de servicio: {error}")