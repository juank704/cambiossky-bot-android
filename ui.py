import os
import cv2
import numpy as np
import subprocess
import mss
import pygetwindow as gw
import time
from fastapi import FastAPI, Form, WebSocket
from fastapi.responses import HTMLResponse
from telethon import TelegramClient
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
import base64
import asyncio

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Inicializar el cliente de Telegram
client = TelegramClient('user', API_ID, API_HASH)

# Inicializar la aplicación FastAPI
middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
]
app = FastAPI(middleware=middleware)

@app.on_event("startup")
async def startup_event():
    await client.start(PHONE_NUMBER)

@app.on_event("shutdown")
async def shutdown_event():
    await client.disconnect()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Telegram Bot Command Sender</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                form {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 20px;
                }
                label, select, input, button {
                    width: 100%;
                    max-width: 500px;  /* Incrementar el ancho máximo */
                    margin: 20px 0;  /* Incrementar el margen */
                    padding: 20px;  /* Incrementar el padding */
                    font-size: 24px;  /* Incrementar el tamaño de la fuente */
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                    font-size: 28px;  /* Incrementar el tamaño de la fuente */
                }
                button:hover {
                    background-color: #45a049;
                }
                table {
                    width: 100%;
                    max-width: 800px;  /* Incrementar el ancho máximo */
                    margin: 40px auto;  /* Incrementar el margen */
                    border-collapse: collapse;
                }
                th, td {
                    padding: 20px;  /* Incrementar el padding */
                    border: 1px solid #ddd;
                    text-align: center;
                    font-size: 20px;  /* Incrementar el tamaño de la fuente */
                }
                @media (max-width: 600px) {
                    label, select, input, button {
                        max-width: 100%;
                        font-size: 30px;  /* Incrementar el tamaño de la fuente para móviles */
                        padding: 25px;  /* Incrementar el padding para móviles */
                    }
                    button {
                        font-size: 32px;  /* Incrementar el tamaño de la fuente para móviles */
                    }
                }
            </style>
            <script>
                const keyDownsByBank = {
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
                };

                function updateFields() {
                    const command = document.getElementById("command").value;
                    const bank = document.getElementById("bank").value;
                    const cuentaField = document.getElementById("cuentaField");
                    const cedulaField = document.getElementById("cedulaField");
                    const clienteField = document.getElementById("clienteField");
                    const montoField = document.getElementById("montoField");
                    const comentarioField = document.getElementById("comentarioField");
                    const destinoField = document.getElementById("destinoField");
                    const submitButton = document.getElementById("submitButton");

                    // Reset all fields
                    cuentaField.style.display = "none";
                    cedulaField.style.display = "none";
                    clienteField.style.display = "none";
                    montoField.style.display = "none";
                    comentarioField.style.display = "none";
                    destinoField.style.display = "none";
                    submitButton.disabled = false;

                    if (command.includes("transfer")) {
                        cuentaField.style.display = "block";
                        montoField.style.display = "block";
                        comentarioField.style.display = "block";

                        if (command === "transfer movil" || bank === "movil") {
                            cedulaField.style.display = "block";
                            destinoField.style.display = "block";
                        }
                    } else if (command.includes("status")) {
                        // No additional fields needed for status
                    } else if (command.includes("client")) {
                        if (["venezuela", "mercantil", "banesco"].includes(bank)) {
                            clienteField.style.display = "block";
                            montoField.style.display = "block";
                            comentarioField.style.display = "block";
                        } else {
                            submitButton.disabled = true;
                        }
                    } else if (command.includes("save")) {
                        cuentaField.style.display = "block";
                        cedulaField.style.display = "block";
                        clienteField.style.display = "block";
                        montoField.style.display = "block";
                        comentarioField.style.display = "block";
                    }
                }

                function onBankChange() {
                    updateFields();
                }

                function sendCommand(event) {
                    event.preventDefault();

                    const formData = new FormData(document.getElementById("commandForm"));

                    fetch("/send_command", {
                        method: "POST",
                        body: formData,
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.status === "success") {
                            addRowToTable(
                                formData.get("command"),
                                formData.get("bank"),
                                formData.get("cuenta"),
                                formData.get("cedula"),
                                formData.get("cliente"),
                                formData.get("monto"),
                                formData.get("comentario"),
                                formData.get("destino")
                            );
                        } else {
                            alert(result.message);
                        }
                    })
                    .catch(error => {
                        alert("Error al enviar el comando: " + error);
                    });
                }

                function addRowToTable(command, bank, cuenta, cedula, cliente, monto, comentario, destino) {
                    const table = document.getElementById("commandTable").getElementsByTagName('tbody')[0];
                    const newRow = table.insertRow();

                    newRow.insertCell(0).innerText = command;
                    newRow.insertCell(1).innerText = bank;
                    newRow.insertCell(2).innerText = cuenta;
                    newRow.insertCell(3).innerText = cedula;
                    newRow.insertCell(4).innerText = cliente;
                    newRow.insertCell(5).innerText = monto;
                    newRow.insertCell(6).innerText = comentario;
                    newRow.insertCell(7).innerText = destino;
                    newRow.insertCell(8).innerText = "Procesando";
                    
                    setTimeout(() => {
                        newRow.cells[8].innerText = "Procesado";
                    }, 300000); // 5 minutes in milliseconds
                }

                function startWebSocket() {
                    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUri = `${protocol}//${location.host}/ws`;
                    ws = new WebSocket(wsUri);
                    ws.onmessage = function(event) {
                        const img = document.getElementById("screen");
                        img.src = "data:image/jpeg;base64," + event.data;
                    };
                }

                window.onload = function() {
                    startWebSocket();
                }
            </script>
        </head>
        <body>
            <h1>Enviar Comandos al Bot de Telegram</h1>
            <form id="commandForm" onsubmit="sendCommand(event)">
                <label for="command">Comando:</label>
                <select id="command" name="command" onchange="updateFields()">
                    <option value="">Selecciona un comando</option>
                    <option value="transfer">transfer</option>
                    <option value="transfer movil">transfer movil</option> <!-- Nueva opción -->
                    <option value="status <banco>">status <banco></option>
                    <option value="client <banco> <cliente> <monto> <comentario>">client <banco> <cliente> <monto> <comentario></option>
                    <option value="save <banco> <cuenta> <cedula> <cliente> <monto> <comentario>">save <banco> <cuenta> <cedula> <cliente> <monto> <comentario></option>
                </select>
                <br><br>
                
                <label for="bank">Banco:</label>
                <select id="bank" name="bank" onchange="onBankChange()">
                    <option value="venezuela">Venezuela</option>
                    <option value="mercantil">Mercantil</option>
                    <option value="banesco">Banesco</option>
                    <option value="movil">Movil</option>
                </select>
                <br><br>

                <div id="cuentaField" style="display:none;">
                    <label for="cuenta">Cuenta:</label>
                    <input type="text" id="cuenta" name="cuenta">
                    <br><br>
                </div>

                <div id="cedulaField" style="display:none;">
                    <label for="cedula">Cédula:</label>
                    <input type="text" id="cedula" name="cedula">
                    <br><br>
                </div>

                <div id="clienteField" style="display:none;">
                    <label for="cliente">Cliente:</label>
                    <input type="text" id="cliente" name="cliente">
                    <br><br>
                </div>

                <div id="montoField" style="display:none;">
                    <label for="monto">Monto:</label>
                    <input type="text" id="monto" name="monto">
                    <br><br>
                </div>

                <div id="comentarioField" style="display:none;">
                    <label for="comentario">Comentario:</label>
                    <input type="text" id="comentario" name="comentario">
                    <br><br>
                </div>

                <div id="destinoField" style="display:none;">
                    <label for="destino">Destino:</label>
                    <select id="destino" name="destino">
                        <option value="0102">0102</option>
                        <option value="0156">0156</option>
                        <option value="0172">0172</option>
                        <option value="0114">0114</option>
                        <option value="0171">0171</option>
                        <option value="0166">0166</option>
                        <option value="0175">0175</option>
                        <option value="0128">0128</option>
                        <option value="0163">0163</option>
                        <option value="0115">0115</option>
                        <option value="0151">0151</option>
                        <option value="0173">0173</option>
                        <option value="0105">0105</option>
                        <option value="0191">0191</option>
                        <option value="0138">0138</option>
                        <option value="0137">0137</option>
                        <option value="0104">0104</option>
                        <option value="0168">0168</option>
                        <option value="0134">0134</option>
                        <option value="0177">0177</option>
                        <option value="0146">0146</option>
                        <option value="0174">0174</option>
                        <option value="0108">0108</option>
                        <option value="0157">0157</option>
                        <option value="0169">0169</option>
                        <option value="0178">0178</option>
                    </select>
                    <br><br>
                </div>

                <button type="submit" id="submitButton">Enviar Comando</button>
            </form>

            <h2>Historial de Comandos</h2>
            <table id="commandTable" border="1">
                <thead>
                    <tr>
                        <th>Comando</th>
                        <th>Banco</th>
                        <th>Cuenta</th>
                        <th>Cédula</th>
                        <th>Cliente</th>
                        <th>Monto</th>
                        <th>Comentario</th>
                        <th>Destino</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>

            <h2>Captura de Pantalla</h2>
            <img id="screen" src="" style="width:100%; max-width:800px; display:block; margin:20px auto;"/>
        </body>
    </html>
    """

@app.post("/send_command")
async def send_command(
    command: str = Form(...),
    bank: str = Form(...),
    cuenta: str = Form(None),
    cedula: str = Form(None),
    cliente: str = Form(None),
    monto: str = Form(None),
    comentario: str = Form(None),
    destino: str = Form(None)  # Nuevo campo
):
    try:
        if command == "client" and bank == "movil":
            return {"status": "error", "message": "El comando 'client' no es aplicable para el banco 'movil'"}
        if command == "transfer":
            if bank in ["movil", "mercantil", "banesco"]:
                command = f"transfer {bank} {cuenta} {cedula} {monto} {comentario}"
            else:
                command = f"transfer {bank} {cuenta} {monto} {comentario}"
        elif command == "transfer movil":
            if not cuenta or not cedula or not monto or not destino:
                return {"status": "error", "message": "Todos los campos son obligatorios para 'transfer movil'"}
            command = f"transfer movil {cuenta} {cedula} {destino} {monto} {comentario}"
        elif command.startswith("status"):
            command = f"status {bank}"
        elif command.startswith("client"):
            if bank in ["venezuela", "mercantil", "banesco"]:
                command = f"client {bank} {cliente} {monto} {comentario}"
            else:
                return {"status": "error", "message": "El comando 'client' solo es aplicable a Venezuela, Mercantil y Banesco"}
        elif command.startswith("save"):
            command = f"save {bank} {cuenta} {cedula} {cliente} {monto} {comentario}"

        channel_id = CHANNEL_ID
        await client.send_message(channel_id, f"/{command}")
        return {"status": "success", "message": f"Comando '{command}' enviado correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    scrcpy_path = 'D:\\development\\scrcpy-win64-v2.5\\scrcpy.exe'
    scrcpy_process = subprocess.Popen([scrcpy_path, '--no-playback', '--no-control'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)

    with mss.mss() as sct:
        while True:
            windows = gw.getWindowsWithTitle('SM-J810M')
            if windows:
                scrcpy_window = windows[0]
                monitor = {
                    'top': scrcpy_window.top,
                    'left': scrcpy_window.left,
                    'width': scrcpy_window.width,
                    'height': scrcpy_window.height,
                    'mon': 1
                }
                img = sct.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Redimensionar la imagen para reducir el tamaño
                frame = cv2.resize(frame, (640, 360))

                # Comprimir la imagen a JPEG con calidad reducida
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                jpeg_bytes = jpeg.tobytes()
                jpeg_base64 = base64.b64encode(jpeg_bytes).decode('utf-8')
                await websocket.send_text(jpeg_base64)
                await asyncio.sleep(0.1)
            else:
                break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
