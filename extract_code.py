import re
import logging

# Configurar el logging
logging.basicConfig(filename='process.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def extract_mercantil_code(message):
    pattern = r"clave temporal: (\d+)"
    match = re.search(pattern, message)
    if match:
        return match.group(1)
    return None

def process_sms(message):
    code = extract_mercantil_code(message)
    if code:
        return code
    return None

if __name__ == "__main__":
    message = "Mercantil informa, clave temporal: 29556170 de Acceso Seguro a Mercantil en Linea Personas, el 10/07/2024 05:03 AM. Si no reconoce llame 02125032423."
    code = process_sms(message)
    if code:
        logging.info(f"Clave temporal de Mercantil: {code}")
    else:
        logging.info("No se pudo obtener la clave temporal.")
