# Используем Ubuntu 22.04 как базовый образ для совместимости с Qt
FROM ubuntu:22.04

# Устанавливаем переменные среды, чтобы избежать интерактивных подсказок во время установки
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Устанавливаем системные зависимости: Python, PyQt5 (через apt для предсобранных бинарников) и другие необходимые инструменты
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-pyqt5 \
    qtwayland5 \
    libgl1-mesa-glx

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости из requirements.txt (PyQt5 уже установлен через apt, но для полноты)
RUN pip3 install -r requirements.txt

# Команда по умолчанию для запуска приложения
CMD ["python3", "main.py"]
