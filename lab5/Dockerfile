FROM python:3.12-slim

# Установка системных зависимостей (Tkinter + libs для matplotlib)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-tk \
        libfontconfig1 \
        libfreetype6 \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements первым (для кэша pip)
COPY requirements.txt .

# Установка Python-пакетов (с таймаутом и без кэша для чистоты)
RUN pip3 install --no-cache-dir --timeout=100 -r requirements.txt

# Копируем код
COPY main.py .

# Запуск GUI
CMD ["python3", "main.py"]
