import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configurar el logging
logging.basicConfig(filename='process.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Token del bot de Telegram
PROFILE_CHROME_DATA = os.getenv("PROFILE_CHROME_DATA")

def get_latest_sms():
    # Configuración de Selenium
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(PROFILE_CHROME_DATA)
    chrome_options.add_argument("--profile-directory=Default")  # Ajusta esto si no estás usando el perfil "Default"
    # chrome_options.add_argument("--headless")  # Ejecuta el navegador en modo headless (comenta esta línea por ahora)

    # Inicializar el controlador de Chrome usando webdriver_manager
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Abre la URL de Google Messages Web
        url = "https://messages.google.com/web/conversations"
        driver.get(url)

        # Espera a que la página cargue (ajusta el tiempo según sea necesario)
        time.sleep(30)  # Aumenta el tiempo de espera si es necesario

        # Encuentra el primer mensaje en la lista de conversaciones
        message = driver.find_element(By.CSS_SELECTOR, "div.snippet-text span.ng-star-inserted")
        if message:
            latest_message = message.text
            logging.info(f"Último mensaje recibido: {latest_message}")
            return latest_message
        else:
            logging.info("No se encontraron mensajes.")
            return None
    except Exception as e:
        logging.error(f"Error al obtener el último mensaje: {e}")
        return None
    finally:
        # Cierra el navegador
        driver.quit()

# Función principal para integrar la obtención del último mensaje en tu script
if __name__ == "__main__":
    latest_sms = get_latest_sms()
    if latest_sms:
        logging.info(f"El último mensaje obtenido es: {latest_sms}")
        # Imprimir explícitamente la salida para que pueda ser capturada
        print(f"Último mensaje: {latest_sms}")
    else:
        logging.info("No se pudo obtener el último mensaje.")
        print("No se pudo obtener el último mensaje.")
