# Dockerfile - вариант 2
FROM ubuntu:22.04

# Установка Python и системных зависимостей
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-pyqt5 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Запуск приложения
CMD ["python3", "main.py"]
