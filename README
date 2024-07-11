# Proyecto de Automatización ADB con Telegram Bot

## Init
```bash
.\env\Scripts\activate
pip install -r requirements.txt
python bot_telegram
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
1. Inicia el bot de Telegram:
   ```bash
   python telegram_bot.py
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