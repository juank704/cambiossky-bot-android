from pynput import mouse, keyboard
import tkinter as tk
import sys
import os

# Configuración de la ventana del ADB en Windows
adb_window_position = (740, 35)  # (x, y) posición de la esquina superior izquierda de la ventana del ADB
adb_window_size = (438, 969)  # (ancho, alto) de la ventana del ADB

# Configuración de la resolución del dispositivo Android
android_resolution = (1080, 2340)  # Resolución de la pantalla del dispositivo Android

# Variables para controlar el estado de escritura y clicks
typing = False
click_detected = False
typed_text = ""

# Función para convertir coordenadas de la ventana del ADB en Windows a coordenadas de Android
def convert_coordinates_to_android(x, y, adb_position, adb_size, android_res):
    adb_x, adb_y = adb_position
    adb_width, adb_height = adb_size
    android_width, android_height = android_res

    # Calcular la posición relativa dentro de la ventana del ADB
    rel_x = x - adb_x
    rel_y = y - adb_y

    # Convertir a coordenadas de Android
    android_x = int(rel_x * android_width / adb_width)
    android_y = int(rel_y * android_height / adb_height)

    return android_x, android_y

# Función para manejar clics del mouse
def on_click(x, y, button, pressed):
    global typing, click_detected, typed_text
    if pressed:
        bank = 'movil'  # Actualiza esto según la subcarpeta que estés utilizando
        coordinates_file_path = f'coordinates/coordinates_{bank}/click_coordinates.txt'
        
        # Crear la carpeta si no existe
        os.makedirs(os.path.dirname(coordinates_file_path), exist_ok=True)
        
        android_x, android_y = convert_coordinates_to_android(x, y, adb_window_position, adb_window_size, android_resolution)
        print(f"Windows: ({x}, {y}), Android: ({android_x}, {android_y})")
        with open(coordinates_file_path, 'a') as file:
            file.write(f"Windows: ({x}, {y}), Android: ({android_x}, {android_y})\n")
        click_detected = True
        if typed_text:
            with open(coordinates_file_path, 'a') as file:
                file.write(f"Windows: keyboard, Android: {typed_text}\n")
            typed_text = ""
        typing = False

# Función para manejar presiones de teclas
def on_press(key):
    global typing, click_detected, typed_text
    try:
        bank = 'movil'  # Actualiza esto según la subcarpeta que estés utilizando
        coordinates_file_path = f'coordinates/coordinates_{bank}/click_coordinates.txt'

        if key == keyboard.Key.left:
            print("Windows: Arrow Key Left")
            start_x, start_y = 900, 1170  # posición inicial del deslizamiento en la pantalla del PC
            end_x, end_y = 200, 1170  # posición final del deslizamiento en la pantalla del PC
            android_start_x, android_start_y = convert_coordinates_to_android(start_x, start_y, adb_window_position, adb_window_size, android_resolution)
            android_end_x, android_end_y = convert_coordinates_to_android(end_x, end_y, adb_window_position, adb_window_size, android_resolution)
            print(f"Android: Swipe from ({android_start_x}, {android_start_y}) to ({android_end_x}, {android_end_y})")
            with open(coordinates_file_path, 'a') as file:
                file.write(f"Windows: Arrow Key Left, Android: Swipe from ({android_start_x}, {android_start_y}) to ({android_end_x}, {android_end_y})\n")
        elif key == keyboard.Key.right:
            print("Windows: Arrow Key Right")
            start_x, start_y = 200, 1170  # posición inicial del deslizamiento en la pantalla del PC
            end_x, end_y = 900, 1170  # posición final del deslizamiento en la pantalla del PC
            android_start_x, android_start_y = convert_coordinates_to_android(start_x, start_y, adb_window_position, adb_window_size, android_resolution)
            android_end_x, android_end_y = convert_coordinates_to_android(end_x, end_y, adb_window_position, adb_window_size, android_resolution)
            print(f"Android: Swipe from ({android_start_x}, {android_start_y}) to ({android_end_x}, {android_end_y})")
            with open(coordinates_file_path, 'a') as file:
                file.write(f"Windows: Arrow Key Right, Android: Swipe from ({android_start_x}, {android_start_y}) to ({android_end_x}, {android_end_y})\n")
        else:
            if not typing and click_detected:
                typing = True
                click_detected = False
            if typing:
                try:
                    typed_text += key.char
                except AttributeError:
                    pass
    except AttributeError:
        pass

# Función para manejar liberación de teclas
def on_release(key):
    global typing, click_detected, typed_text
    if key == keyboard.Key.esc:
        # Dejar de escuchar si se presiona la tecla Escape
        return False

# Función para imprimir la posición del mouse en la misma línea
def print_mouse_position(x, y):
    sys.stdout.write(f"\rPosición del mouse: ({x}, {y})")
    sys.stdout.flush()

# Función para manejar el movimiento del mouse
def on_move(x, y):
    print_mouse_position(x, y)

# Configurar los listeners
mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

# Iniciar los listeners
mouse_listener.start()
keyboard_listener.start()

# Mantener el script en ejecución
mouse_listener.join()
keyboard_listener.join()