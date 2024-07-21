# Proyecto de Automatización ADB con Telegram Bot

## Setup Local
```bash
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
choco install scrcpy
choco install adb
python bot_telegram.py
   ```

## Configuración Rápida de Docker con WSL y USB
Ejecuta los siguientes comandos en PowerShell como administrador para habilitar WSL, configurar WSL 2, instalar Ubuntu, conectar un dispositivo USB y levantar servicios con Docker:

```bash
# Habilitar WSL y la Plataforma de Máquina Virtual
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Configurar WSL 2 por defecto
wsl --set-default-version 2

# Instalar Ubuntu (descargar desde la Microsoft Store si no está instalado)

# Instalar usbipd-win

# Conectar dispositivo USB a WSL
usbipd list
usbipd wsl attach --busid <busid>
usbipd attach --busid <busid> --wsl Ubuntu

# Ejecutar contenedor Docker con acceso USB
docker run --rm --network host --privileged --device=/dev/bus/usb/001/002 adb-docker

# Construir y levantar servicios con Docker Compose
docker-compose build
docker-compose up
   ```

## Descripción
Este proyecto permite automatizar comandos ADB a través de un bot de Telegram. Los usuarios pueden enviar comandos específicos al bot para realizar diversas acciones en dispositivos Android, como tocar elementos de la pantalla, realizar capturas de pantalla, cerrar aplicaciones y más. El proyecto también incluye la capacidad de procesar archivos de texto con instrucciones para ejecutar comandos ADB secuencialmente.

## Características
- Recepción de comandos ADB a través de un bot de Telegram.
- Automatización de tareas en dispositivos Android.
- Generación de capturas de pantalla.
- Ejecución de scripts personalizados para acciones específicas.
- Navegación en listas y selección de elementos en función de códigos de destino.
- Manejador de archivos de bloqueo para evitar la ejecución simultánea de múltiples instancias.

## Requisitos
- Python 3.6 o superior.
- ADB (Android Debug Bridge) instalado y configurado en el PATH del sistema.
- Una cuenta de bot de Telegram con su correspondiente token de acceso.
- Librerías de Python:
  - `python-telegram-bot`
  - `Pillow`

## Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/adb-telegram-bot.git
   cd adb-telegram-bot
   ```

2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv env
   source env/bin/activate  # En Windows usa `env\Scripts\activate`
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura el token del bot de Telegram en el archivo principal (`telegram_bot.py`):
   ```python
   TELEGRAM_BOT_TOKEN = "TU_TOKEN_DE_TELEGRAM"
   ```

## Uso
1. Inicia el bot de Telegram y webpage:
   ```bash
   python telegram_bot_polling.py
   uvicorn ui:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Envía comandos al bot de Telegram según el siguiente formato:
   - `transfer <banco> <cuenta> <cedula> <monto> <comentario>` para Mercantil, Banesco o Movil.
   - `transfer <banco> <cuenta> <monto> <comentario>` para otros bancos.
   - `status <banco>` para verificar el estado.
   - `client <banco> <cliente> <monto> <comentario>` para registrar un nuevo cliente.
   - `save <banco> <cuenta> <cedula> <cliente> <monto> <comentario>` para guardar información del cliente.

## Estructura del Proyecto
- `telegram_bot.py`: Archivo principal que configura y ejecuta el bot de Telegram.
- `adb_generator.py`: Script que procesa los archivos de instrucciones y ejecuta comandos ADB.
- `coordinates/`: Carpeta que contiene archivos de instrucciones específicas para cada banco.
- `screenshot/`: Carpeta donde se guardan las capturas de pantalla generadas por los comandos.

## Ejemplo de Uso
Para enviar un comando de transferencia a través del bot de Telegram:
```plaintext
transfer banesco 1234567890 12345678 1000 "Pago de servicios"
```
Para verificar el estado de un banco:
```plaintext
status mercantil
```

## Notas
- Asegúrate de tener el dispositivo Android conectado y en modo depuración USB.
- Verifica que ADB esté correctamente configurado y pueda comunicarse con el dispositivo.

## Contribuciones
Las contribuciones son bienvenidas. Puedes abrir un issue o enviar un pull request con tus mejoras y correcciones.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.