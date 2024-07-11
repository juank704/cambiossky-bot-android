import re
import time
import os
import sys
import subprocess
import logging
from datetime import datetime

# Configurar el logging
logging.basicConfig(filename='process.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lista de bancos para crear carpetas
banks = [
    'banesco',
    'bicentenario',
    'bnc',
    'mercantil',
    'provincial',
    'venezuela',
    'movil'
]

# Crear las carpetas 'coordinates' y 'screenshot' con subcarpetas correspondientes
base_coordinates_folder = 'coordinates'
base_screenshot_folder = 'screenshot'
os.makedirs(base_coordinates_folder, exist_ok=True)
os.makedirs(base_screenshot_folder, exist_ok=True)
for bank in banks:
    os.makedirs(os.path.join(base_coordinates_folder, f'coordinates_{bank}'), exist_ok=True)
    os.makedirs(os.path.join(base_screenshot_folder, f'screenshot_{bank}'), exist_ok=True)

# Diccionario para los códigos de bancos y sus correspondientes números de keydowns
key_downs_by_bank = {
    '0102': 0,
    '0156': 1,
    '0172': 2,
    '0114': 3,
    '0171': 4,
    '0166': 5,
    '0175': 6,
    '0128': 7,
    '0163': 8,
    '0115': 9,
    '0151': 10,
    '0173': 11,
    '0105': 12,
    '0191': 13,
    '0138': 14,
    '0137': 15,
    '0104': 16,
    '0168': 17,
    '0134': 18,
    '0177': 19,
    '0146': 20,
    '0174': 21,
    '0108': 22,
    '0157': 23,
    '0169': 24,
    '0178': 25
}

# Función para generar comandos ADB para presionar el botón "Recientes" y luego el botón "Cerrar todo"
def close_all_apps_with_keyevents():
    commands = [
        "adb shell input keyevent 187",  # Presionar botón "Recientes"
        "adb shell input tap 549 1840"   # Presionar botón "Cerrar todo" (ajusta estas coordenadas si es necesario)
    ]
    return commands

# Función para simular navegación en la lista usando keyevents
def navigate_list(destination_code, delay):
    commands = []
    key_downs = key_downs_by_bank.get(destination_code, 0)
    if destination_code == '0102':
        # Si el banco es Banco de Venezuela (0102), hacer un DPAD_UP
        commands.append((f"adb shell input keyevent DPAD_UP", delay))
    else:
        for _ in range(key_downs):
            commands.append((f"adb shell input keyevent DPAD_DOWN", delay))
    commands.append((f"adb shell input keyevent DPAD_CENTER", delay))  # Seleccionar el elemento
    return commands

# Función para procesar una línea del archivo y generar el comando ADB correspondiente
def process_line(line, bank):
    adb_commands = []
    delay = 2  # Valor predeterminado del delay
    screenshot_filename = "screenshot.png"  # Nombre de archivo predeterminado para la captura de pantalla

    # Expresiones regulares para detectar diferentes tipos de instrucciones
    click_pattern = re.compile(r"Android: \((\d+), (\d+)\)")
    swipe_pattern = re.compile(r"Swipe from \((\-?\d+), (\-?\d+)\) to \((\-?\d+), (\-?\d+)\)")
    keyboard_pattern = re.compile(r"Android: (.+)")
    windows_screenshot_pattern = re.compile(r"Windows: screenshot")
    android_screenshot_pattern = re.compile(r"Android: screenshot")
    open_app_pattern = re.compile(r"open whatsapp")
    close_all_apps_pattern = re.compile(r"close all apps")
    home_pattern = re.compile(r"Windows: home, Android: home")
    delay_pattern = re.compile(r"delay=(\d+)")
    escape_pattern = re.compile(r"Android: escape")
    sms_pattern = re.compile(r"Windows: sms")
    destino_pattern = re.compile(r"Android: destino_(\d{4})")

    # Detectar y extraer el parámetro delay si está presente
    delay_match = delay_pattern.search(line)
    if delay_match:
        delay = int(delay_match.group(1))

    if windows_screenshot_pattern.search(line):
        # Instrucción para tomar una captura de pantalla en Windows con nombre específico y timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f'screenshot/screenshot_{bank}/{bank}_{timestamp}.png'
        logging.info(screenshot_filename)
        adb_commands.append((f"adb exec-out screencap -p > {screenshot_filename}", delay))
    
    elif android_screenshot_pattern.search(line):
        # Instrucción para tomar una captura de pantalla en dispositivos Samsung
        adb_commands.append((f"adb shell input keyevent 120", delay))
    
    elif escape_pattern.search(line):
        # Instrucción para ocultar el teclado
        adb_commands.append((f"adb shell input keyevent 111", delay))
    
    elif sms_pattern.search(line):
        # Instrucción para obtener la clave temporal de Mercantil
        adb_commands.append((f"execute_sms", delay))  # Agregar un marcador para ejecutar el script de SMS más tarde
    
    elif "Windows: (" in line and "Android: (" in line:
        # Instrucción de clic
        match = click_pattern.search(line)
        if match:
            x, y = match.groups()
            adb_commands.append((f"adb shell input tap {x} {y}", delay))
    
    elif "Arrow Key Right" in line:
        # Instrucción de deslizamiento a la derecha
        x1, y1, x2, y2 = 100, 1170, 1000, 1170
        adb_commands.append((f"adb shell input swipe {x1} {y1} {x2} {y2}", delay))
    
    elif "Arrow Key Left" in line:
        # Instrucción de deslizamiento a la izquierda
        x1, y1, x2, y2 = 1000, 1170, 100, 1170
        adb_commands.append((f"adb shell input swipe {x1} {y1} {x2} {y2}", delay))
    
    elif "Windows: keyboard, Android:" in line:
        # Instrucción de teclado
        match = keyboard_pattern.search(line)
        if match:
            text = match.group(1)
            adb_commands.append((f"adb shell input text '{text}'", delay))
    
    elif "Windows: open whatsapp, Android: open whatsapp" in line:
        # Instrucción para abrir WhatsApp
        adb_commands.append((f"adb shell monkey -p com.whatsapp -c android.intent.category.LAUNCHER 1", delay))
    
    elif close_all_apps_pattern.search(line):
        # Instrucción para cerrar todas las aplicaciones usando los botones "Recientes" y "Cerrar todo"
        adb_commands.extend((cmd, delay) for cmd in close_all_apps_with_keyevents())
    
    elif home_pattern.search(line):
        # Instrucción para presionar el botón Home
        adb_commands.append((f"adb shell input keyevent 3", delay))
    
    # Manejar destino_{destino}
    match = destino_pattern.search(line)
    if match:
        destino = match.group(1)
        if destino in key_downs_by_bank:
            adb_commands.extend(navigate_list(destino, delay))
    
    return adb_commands

# Función para leer el archivo y generar los comandos ADB
def generate_adb_commands(file_path, bank):
    adb_commands = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            logging.info(f"Leyendo línea: {line.strip()}")
            commands = process_line(line.strip(), bank)
            if commands:
                logging.info(f"Procesando línea: {line.strip()}")
                adb_commands.extend(commands)
                for cmd, cmd_delay in commands:
                    logging.info(f"Generado comando: {cmd} con delay de {cmd_delay} segundos")
    
    return adb_commands

# Función para ejecutar el script get_sms.py y obtener la clave temporal
def execute_sms_script():
    logging.info("Ejecutando proceso para obtener la clave temporal...")
    # Especifica el intérprete de Python del entorno virtual
    python_executable = os.path.abspath("env/Scripts/python.exe")
    result = subprocess.run([python_executable, "get_sms.py"], capture_output=True, text=True)
    if result.returncode == 0:
        logging.info("El script get_sms.py se ejecutó correctamente")
        for output_line in result.stdout.splitlines():
            logging.info(f"Salida del script: {output_line}")
            if "clave temporal:" in output_line.lower():
                # Usar una expresión regular para capturar el número de la clave temporal
                match = re.search(r"clave temporal: (\d+)", output_line.lower())
                if match:
                    code = match.group(1).strip()
                    logging.info(f"Clave temporal encontrada: {code}")
                    return code
    logging.error(f"El script get_sms.py falló con el siguiente error: {result.stderr}")
    return None

# Función para escribir texto en ADB lentamente
def slow_adb_text_input(text, delay=0.05):
    for char in text:
        if char == ' ':
            os.system("adb shell input keyevent 62")  # Código de la tecla de la barra espaciadora
        else:
            os.system(f"adb shell input text '{char}'")
        time.sleep(delay)

# Función para ejecutar los comandos ADB generados con el delay especificado
def execute_adb_commands(adb_commands):
    for command, delay in adb_commands:
        if command == "execute_sms":
            code = execute_sms_script()
            if code:
                logging.info(f"Ejecutando: adb shell input text '{code}' con delay de {delay} segundos")
                slow_adb_text_input(code)  # Usar la función de entrada lenta
                time.sleep(delay)
            else:
                logging.error("No se pudo obtener la clave temporal.")
        elif "adb shell input text" in command:
            text = command.split("'")[1]
            logging.info(f"Ejecutando: {command} con delay de {delay} segundos")
            slow_adb_text_input(text)  # Usar la función de entrada lenta
            time.sleep(delay)
        else:
            logging.info(f"Ejecutando: {command} con delay de {delay} segundos")
            os.system(command)
            # Añadir un mayor delay después del comando de captura de pantalla para asegurar que se guarde correctamente
            if "keyevent 120" in command:
                time.sleep(5)  # Puedes ajustar este valor según sea necesario
            else:
                time.sleep(delay)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Uso: python adb_generator.py <banco> <ruta_del_archivo_de_instrucciones>")
        sys.exit(1)

    bank = sys.argv[1]
    file_path = sys.argv[2]

    # Generar los comandos ADB
    adb_commands = generate_adb_commands(file_path, bank)

    # Ejecutar los comandos ADB con el delay especificado
    execute_adb_commands(adb_commands)
