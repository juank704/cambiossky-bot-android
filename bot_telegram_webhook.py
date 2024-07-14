import os
import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import subprocess
from PIL import Image
import tempfile
import shlex
import sys

# Cargar las variables del archivo .env
load_dotenv()

# Configurar logging para que escriba en un archivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Obtener el token del bot de Telegram y la URL del webhook desde las variables de entorno
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    logger.error("TELEGRAM_BOT_TOKEN o WEBHOOK_URL no están configurados correctamente en el archivo .env")
    sys.exit(1)

# Define las palabras que quieres reemplazar
replace = "password"

# Lista de bancos permitidos
banks = ['venezuela', 'banesco', 'mercantil', 'provincial', 'bnc', 'bicentenario', 'movil']

# Variable de estado para evitar el procesamiento duplicado
is_processing = False

# Función para obtener la contraseña específica del banco
def get_password_for_bank(bank):
    return os.getenv(f"password_{bank}")

# Inicializar la aplicación de Telegram
ptb = (
    Application.builder()
    .updater(None)
    .token(TELEGRAM_TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb.bot.set_webhook(WEBHOOK_URL)
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

# Inicializar la aplicación FastAPI
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

# Función para encontrar la última imagen en la carpeta específica de screenshots
def get_latest_screenshot(bank):
    screenshot_folder = f'screenshot/screenshot_{bank}'
    files = [os.path.join(screenshot_folder, f) for f in os.listdir(screenshot_folder) if os.path.isfile(os.path.join(screenshot_folder, f))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

# Función para redimensionar la imagen
def resize_image(image_path, bank, max_size=(800, 800)):
    screenshot_folder = f'screenshot/screenshot_{bank}'
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        resized_path = os.path.join(screenshot_folder, 'resized_' + os.path.basename(image_path))
        img.save(resized_path)
        return resized_path

# Función para leer y reemplazar variables en una plantilla
def read_and_replace_template(file_path, **kwargs):
    with open(file_path, 'r') as file:
        content = file.read()
    return content.format(**kwargs)

# Función para iniciar el bot y enviar un mensaje de bienvenida
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('¡Hola! Envíame "transfer <banco> <cuenta> <cedula> <monto> <comentario>" para Mercantil o Banesco, o "transfer <banco> <cuenta> <monto> <comentario>" para otros bancos. También puedes usar "status <banco>" para ejecutar el script adb_generator.py. Envíame "client <banco> <cliente> <monto> <comentario>" para registrar un nuevo cliente.')

# Función para manejar el comando "transfer"
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing

    # Evitar procesamiento duplicado
    if is_processing:
        await update.message.reply_text("Ya estoy procesando otro comando. Por favor espera.")
        return

    try:
        is_processing = True
        message_text = update.message.text.lower()
        await handle_transfer_command(update, context, message_text)
    except Exception as e:
        await update.message.reply_text(f"Error al procesar el comando: {e}")
    finally:
        is_processing = False

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing

    # Evitar procesamiento duplicado
    if is_processing:
        await update.message.reply_text("Ya estoy procesando otro comando. Por favor espera.")
        return

    try:
        is_processing = True
        message_text = update.message.text.lower()
        await handle_status_command(update, context, message_text)
    except Exception as e:
        await update.message.reply_text(f"Error al procesar el comando: {e}")
    finally:
        is_processing = False

# Función para manejar el comando "client"
async def client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing

    # Evitar procesamiento duplicado
    if is_processing:
        await update.message.reply_text("Ya estoy procesando otro comando. Por favor espera.")
        return

    try:
        is_processing = True
        message_text = update.message.text.lower()
        await handle_client_command(update, context, message_text)
    except Exception as e:
        await update.message.reply_text(f"Error al procesar el comando: {e}")
    finally:
        is_processing = False

# Función para manejar el comando "save"
async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing

    # Evitar procesamiento duplicado
    if is_processing:
        await update.message.reply_text("Ya estoy procesando otro comando. Por favor espera.")
        return

    try:
        is_processing = True
        message_text = update.message.text.lower()
        await handle_save_command(update, context, message_text)
    except Exception as e:
        await update.message.reply_text(f"Error al procesar el comando: {e}")
    finally:
        is_processing = False

# Función para manejar el comando "transfer"
async def handle_transfer_command(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    try:
        parts = shlex.split(message_text)
        if len(parts) < 5:
            await update.message.reply_text("Formato incorrecto. Por favor usa: 'transfer <banco> <cuenta> <monto> <comentario>' o 'transfer <banco> <cuenta> <cedula> <monto> <comentario>' para Mercantil o Banesco.")
            return
        
        bank = parts[1]
        if bank not in banks:
            await update.message.reply_text(f"Banco no reconocido. Bancos disponibles: {', '.join(banks)}")
            return

        password = get_password_for_bank(bank)
        if not password:
            await update.message.reply_text(f"No se encontró la contraseña para el banco {bank}.")
            return

        if bank in ['mercantil', 'banesco']:
            if len(parts) != 6:
                await update.message.reply_text(f"Formato incorrecto para {bank}. Por favor usa: 'transfer {bank} <cuenta> <cedula> <monto> <comentario>'.")
                return
            cuenta, cedula, monto, comentario = parts[2], parts[3], parts[4], parts[5]
            coordinates_file_path = f'coordinates/coordinates_{bank}/transfer.txt'
            new_content = read_and_replace_template(coordinates_file_path, cuenta=cuenta, cedula=cedula, monto=monto, comentario=comentario)
        elif bank == 'movil':
            if len(parts) != 7:
                await update.message.reply_text(f"Formato incorrecto para {bank}. Por favor usa: 'transfer movil <cuenta> <cedula> <destino> <monto> <comentario>'.")
                return
            cuenta, cedula, destino, monto, comentario = parts[2], parts[3], parts[4], parts[5], parts[6]
            coordinates_file_path = f'coordinates/coordinates_{bank}/transfer.txt'
            new_content = read_and_replace_template(coordinates_file_path, cuenta=cuenta, cedula=cedula, destino=destino, monto=monto, comentario=comentario)
        else:
            if len(parts) != 5:
                await update.message.reply_text(f"Formato incorrecto para {bank}. Por favor usa: 'transfer {bank} <cuenta> <monto> <comentario>'.")
                return
            cuenta, monto, comentario = parts[2], parts[3], parts[4]
            coordinates_file_path = f'coordinates/coordinates_{bank}/transfer.txt'
            new_content = read_and_replace_template(coordinates_file_path, cuenta=cuenta, monto=monto, comentario=comentario)

    except ValueError:
        await update.message.reply_text("Formato incorrecto. Por favor usa: 'transfer <banco> <cuenta> <monto> <comentario>' o 'transfer <banco> <cuenta> <cedula> <monto> <comentario>' para Mercantil o Banesco.")
        return

    # Crear un archivo temporal con el contenido actualizado
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(new_content)

    # Leer el contenido del archivo temporal
    with open(temp_file_path, 'r') as temp_file:
        content = temp_file.read()
        new_content = content.replace(replace, password)

    # Escribir el contenido actualizado en el mismo archivo temporal
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(new_content)

    # Ejecutar el script adb_generator.py con el archivo de coordenadas correspondiente
    await run_adb_script(update, context, bank, temp_file_path)

    # Eliminar el archivo temporal después de usarlo
    os.remove(temp_file_path)

# Función para manejar el comando "status"
async def handle_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    try:
        _, bank = message_text.split(maxsplit=1)
        if bank not in banks:
            await update.message.reply_text(f"Banco no reconocido. Bancos disponibles: {', '.join(banks)}")
            return
    except ValueError:
        await update.message.reply_text("Formato incorrecto. Por favor usa: 'status <banco>'")
        return

    password = get_password_for_bank(bank)
    if not password:
        await update.message.reply_text(f"No se encontró la contraseña para el banco {bank}.")
        return

    # Crear archivo status.txt con el contenido específico para verificar el estado usando la plantilla específica del banco
    coordinates_file_path = f'coordinates/coordinates_{bank}/status.txt'
    new_content = read_and_replace_template(coordinates_file_path)

    # Crear un archivo temporal con el contenido actualizado
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(new_content)

    # Leer el contenido del archivo temporal
    with open(temp_file_path, 'r') as temp_file:
        content = temp_file.read()
        new_content = content.replace(replace, password)

    # Escribir el contenido actualizado en el mismo archivo temporal
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(new_content)

    # Ejecutar el script adb_generator.py con el archivo de coordenadas correspondiente
    await run_adb_script(update, context, bank, temp_file_path)

    # Eliminar el archivo temporal después de usarlo
    os.remove(temp_file_path)

# Función para manejar el comando "client"
async def handle_client_command(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    try:
        parts = shlex.split(message_text)
        if len(parts) != 5:
            await update.message.reply_text("Formato incorrecto. Por favor usa: 'client <banco> <cliente> <monto> <comentario>'.")
            return
        
        bank = parts[1]
        if bank not in banks:
            await update.message.reply_text(f"Banco no reconocido. Bancos disponibles: {', '.join(banks)}")
            return

        password = get_password_for_bank(bank)
        if not password:
            await update.message.reply_text(f"No se encontró la contraseña para el banco {bank}.")
            return

        cliente, monto, comentario = parts[2], parts[3], parts[4]
        coordinates_file_path = f'coordinates/coordinates_{bank}/client.txt'
        new_content = read_and_replace_template(coordinates_file_path, cliente=cliente, monto=monto, comentario=comentario)

    except ValueError:
        await update.message.reply_text("Formato incorrecto. Por favor usa: 'client <banco> <cliente> <monto> <comentario>'.")
        return

    # Crear un archivo temporal con el contenido actualizado
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(new_content)

    # Leer el contenido del archivo temporal
    with open(temp_file_path, 'r') as temp_file:
        content = temp_file.read()
        new_content = content.replace(replace, password)

    # Escribir el contenido actualizado en el mismo archivo temporal
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(new_content)

    # Ejecutar el script adb_generator.py con el archivo de coordenadas correspondiente
    await run_adb_script(update, context, bank, temp_file_path)

    # Eliminar el archivo temporal después de usarlo
    os.remove(temp_file_path)

# Función para manejar el comando "save"
async def handle_save_command(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    try:
        parts = shlex.split(message_text)
        if len(parts) != 7:
            await update.message.reply_text("Formato incorrecto. Por favor usa: 'save <banco> <cuenta> <cedula> <cliente> <monto> <comentario>'.")
            return
        
        bank = parts[1]
        if bank not in banks:
            await update.message.reply_text(f"Banco no reconocido. Bancos disponibles: {', '.join(banks)}")
            return

        password = get_password_for_bank(bank)
        if not password:
            await update.message.reply_text(f"No se encontró la contraseña para el banco {bank}.")
            return

        cuenta, cedula, cliente, monto, comentario = parts[2], parts[3], parts[4], parts[5], parts[6]
        coordinates_file_path = f'coordinates/coordinates_{bank}/save.txt'
        new_content = read_and_replace_template(coordinates_file_path, cuenta=cuenta, cedula=cedula, cliente=cliente, monto=monto, comentario=comentario)

    except ValueError:
        await update.message.reply_text("Formato incorrecto. Por favor usa: 'save <banco> <cuenta> <cedula> <cliente> <monto> <comentario>'.")
        return

    # Crear un archivo temporal con el contenido actualizado
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(new_content)

    # Leer el contenido del archivo temporal
    with open(temp_file_path, 'r') as temp_file:
        content = temp_file.read()
        new_content = content.replace(replace, password)

    # Escribir el contenido actualizado en el mismo archivo temporal
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(new_content)

    # Ejecutar el script adb_generator.py con el archivo de coordenadas correspondiente
    await run_adb_script(update, context, bank, temp_file_path)

    # Eliminar el archivo temporal después de usarlo
    os.remove(temp_file_path)

async def run_adb_script(update: Update, context: ContextTypes.DEFAULT_TYPE, bank, temp_file_path):
    lock_file = f'{bank}.lock'
    if os.path.exists(lock_file):
        await update.message.reply_text(f"Ya hay un proceso en ejecución para el banco {bank}. Por favor, espera a que termine.")
        return

    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        subprocess.run(['python', 'adb_generator.py', bank, temp_file_path], capture_output=True, text=True)
        
        latest_screenshot = get_latest_screenshot(bank)
        if (latest_screenshot):
            resized_screenshot = resize_image(latest_screenshot, bank)
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=open(resized_screenshot, 'rb'))
        else:
            await update.message.reply_text("No se encontró ninguna captura de pantalla.")
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)

# Agregar manejadores
ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(CommandHandler("transfer", transfer))
ptb.add_handler(CommandHandler("status", status))
ptb.add_handler(CommandHandler("client", client))
ptb.add_handler(CommandHandler("save", save))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
