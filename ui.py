import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from telethon import TelegramClient
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
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

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            <script>
                function updateFields() {
                    const command = document.getElementById("command").value;
                    const bank = document.getElementById("bank").value;
                    const cuentaField = document.getElementById("cuentaField");
                    const cedulaField = document.getElementById("cedulaField");
                    const clienteField = document.getElementById("clienteField");
                    const montoField = document.getElementById("montoField");
                    const comentarioField = document.getElementById("comentarioField");
                    const submitButton = document.getElementById("submitButton");

                    // Reset all fields
                    cuentaField.style.display = "none";
                    cedulaField.style.display = "none";
                    clienteField.style.display = "none";
                    montoField.style.display = "none";
                    comentarioField.style.display = "none";
                    submitButton.disabled = false;

                    if (command.includes("transfer")) {
                        cuentaField.style.display = "block";
                        montoField.style.display = "block";
                        comentarioField.style.display = "block";

                        if (bank === "movil" || bank === "mercantil" || bank === "banesco") {
                            cedulaField.style.display = "block";
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
                                formData.get("comentario")
                            );
                        } else {
                            alert(result.message);
                        }
                    })
                    .catch(error => {
                        alert("Error al enviar el comando: " + error);
                    });
                }

                function addRowToTable(command, bank, cuenta, cedula, cliente, monto, comentario) {
                    const table = document.getElementById("commandTable").getElementsByTagName('tbody')[0];
                    const newRow = table.insertRow();

                    newRow.insertCell(0).innerText = command;
                    newRow.insertCell(1).innerText = bank;
                    newRow.insertCell(2).innerText = cuenta;
                    newRow.insertCell(3).innerText = cedula;
                    newRow.insertCell(4).innerText = cliente;
                    newRow.insertCell(5).innerText = monto;
                    newRow.insertCell(6).innerText = comentario;
                    newRow.insertCell(7).innerText = "Procesando";
                    
                    setTimeout(() => {
                        newRow.cells[7].innerText = "Procesado";
                    }, 300000); // 5 minutes in milliseconds
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
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
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
    comentario: str = Form(None)
):
    try:
        # Validar que el comando 'client' no sea usado con el banco 'movil'
        if command == "client" and bank == "movil":
            return {"status": "error", "message": "El comando 'client' no es aplicable para el banco 'movil'"}

        # Construye el comando basándote en el formulario
        if command == "transfer":
            if bank in ["movil", "mercantil", "banesco"]:
                command = f"transfer {bank} {cuenta} {cedula} {monto} {comentario}"
            else:
                command = f"transfer {bank} {cuenta} {monto} {comentario}"
        elif command.startswith("status"):
            command = f"status {bank}"
        elif command.startswith("client"):
            if bank in ["venezuela", "mercantil", "banesco"]:
                command = f"client {bank} {cliente} {monto} {comentario}"
            else:
                return {"status": "error", "message": "El comando 'client' solo es aplicable a Venezuela, Mercantil y Banesco"}
        elif command.startswith("save"):
            command = f"save {bank} {cuenta} {cedula} {cliente} {monto} {comentario}"

        channel_id = CHANNEL_ID  # Reemplaza con el ID o nombre de usuario real de tu bot
        await client.send_message(channel_id, f"/{command}")
        return {"status": "success", "message": f"Comando '{command}' enviado correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Cambia a un puerto diferente si 8000 está en uso
