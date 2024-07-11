import os
import signal

def terminate_process(pid):
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Proceso {pid} terminado correctamente.")
    except OSError as e:
        print(f"Error al terminar el proceso {pid}: {e}")

# Ejemplo de uso
terminate_process(28396)