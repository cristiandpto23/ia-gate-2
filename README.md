# Proyecto IA (GATE 2)

Aplicación de consola en Python que envía preguntas a la API de Gemini y muestra una respuesta breve en formato JSON, con categoría y nivel de confianza.

## Requisitos

- Python 3.12 o superior.
- Una clave de API de Gemini.

## Configuración

Los ejemplos incluyen comandos para PowerShell en Windows y para una shell de Linux.

1. Clona el repositorio y entra en su carpeta raíz.
2. Crea y activa un entorno virtual (opcional si usas `uv`). En PowerShell:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   En Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala el proyecto y sus dependencias con `pip` (el comando es igual en PowerShell y Linux):

   ```powershell
   python -m pip install -r requirements.txt
   ```

   O con `uv`:

   ```powershell
   uv sync
   ```

4. Copia `.env.example` a `.env` y agrega tu clave de Gemini:

   ```env
   GEMINI_API_KEY=tu_clave_de_gemini
   ```

   No compartas ni subas `.env`; está excluido de Git.

## Ejecución

Desde la raíz del proyecto y con el entorno virtual activado, en PowerShell o Linux:

```powershell
python main.py
```

El programa consulta Gemini con dos preguntas de ejemplo e imprime las respuestas y el costo estimado a partir del uso de tokens informado por la API.

## Estructura

```text
.
├── main.py                    # Ejemplo ejecutable
├── src/proyecto_ia/           # Paquete de Python
│   └── consumir_gemini.py     # Construcción de solicitudes y manejo de respuestas
├── prompts/                   # Banco de prompts y experimento de consistencia
├── docs/                      # Documentación del proyecto
├── tests/                     # Espacio para pruebas automatizadas
├── .env.example               # Plantilla de configuración local
├── pyproject.toml             # Metadatos y dependencias del paquete
└── requirements.txt           # Instalación reproducible con pip
```
