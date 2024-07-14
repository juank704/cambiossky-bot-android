# Usa una imagen base de Python
FROM python:3.12

# Instala ADB en el contenedor
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    x11vnc \
    fluxbox \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    curl \
    linux-headers-amd64 \
    build-essential \
    gcc \
    xauth \
    android-tools-adb \
    && apt-get clean

# Instala Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Instala ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q --no-check-certificate -O /tmp/chromedriver_linux64.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver_linux64.zip

# Copia el archivo requirements.txt en el contenedor
COPY requirements.txt /app/requirements.txt
# Instala las dependencias de Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia el contenido de tu aplicación
COPY . /app

# Establece el directorio de trabajo
WORKDIR /app

# Expon el puerto del servidor Flask (si lo usas para otra cosa)
EXPOSE 5000

# Ejecuta el script de Python
CMD ["python", "bot_telegram.py"]
