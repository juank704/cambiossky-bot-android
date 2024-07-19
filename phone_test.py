import subprocess

def adb_command(command):
    """Ejecuta un comando adb y devuelve la salida."""
    result = subprocess.run(['adb'] + command.split(), capture_output=True, text=True)
    return result.stdout.strip()

def list_devices():
    """Lista todos los dispositivos conectados."""
    print("Listando dispositivos conectados:")
    output = adb_command('devices')
    print(output)

def get_device_info():
    """Obtiene información del dispositivo."""
    print("Información del dispositivo:")
    model = adb_command('shell getprop ro.product.model')
    manufacturer = adb_command('shell getprop ro.product.manufacturer')
    print(f"Modelo: {model}")
    print(f"Fabricante: {manufacturer}")

def reboot_device():
    """Reinicia el dispositivo."""
    print("Reiniciando el dispositivo...")
    adb_command('reboot')
    print("El dispositivo se está reiniciando...")

def click_position(x, y):
    """Hace clic en una posición específica de la pantalla."""
    print(f"Haciendo clic en la posición ({x}, {y})")
    adb_command(f'shell input tap {x} {y}')
    print(f"Se ha hecho clic en la posición ({x}, {y})")

def perform_custom_action():
    """Ejecuta una acción personalizada."""
    print("Ejecutando acción personalizada...")
    # Aquí puedes agregar más comandos personalizados
    adb_command('shell input swipe 500 500 500 1000')  # Ejemplo de un gesto de swipe
    print("Se ha ejecutado la acción personalizada.")

def main():
    while True:
        print("\nOpciones:")
        print("1. Listar dispositivos")
        print("2. Obtener información del dispositivo")
        print("3. Reiniciar dispositivo")
        print("4. Hacer clic en una posición específica")
        print("5. Ejecutar acción personalizada")
        print("6. Salir")
        choice = input("Selecciona una opción: ")

        if choice == '1':
            list_devices()
        elif choice == '2':
            get_device_info()
        elif choice == '3':
            reboot_device()
        elif choice == '4':
            x = input("Ingresa la coordenada X: ")
            y = input("Ingresa la coordenada Y: ")
            click_position(x, y)
        elif choice == '5':
            perform_custom_action()
        elif choice == '6':
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")

if __name__ == "__main__":
    main()
