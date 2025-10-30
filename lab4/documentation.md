# Лабораторная работа 4: Базовые растровые алгоритмы

## Описание
Приложение демонстрирует работу пяти базовых растровых алгоритмов:
1. **Пошаговый алгоритм** - простейший алгоритм растеризации отрезков
2. **Алгоритм ЦДА** (Digital Differential Analyzer) - алгоритм цифрового дифференциального анализатора 
3. **Алгоритм Брезенхема** для отрезков - эффективный целочисленный алгоритм
4. **Алгоритм Брезенхема** для окружностей - оптимизированный алгоритм для рисования окружностей
5. **Алгоритм Кастла-Питвея (Wu)** - алгоритм сглаживания линий с антиалиасингом

## Установка и запуск

### Требования
- Python 3.7+
- PyQt5

### Установка зависимостей
pip install -r requirements.txt

## Контейнеризация
Образ доступен на Docker Hub: timojj/raster-algorithms-lab

Чтобы запустить:
docker pull timojj/raster-algorithms-lab
docker run -it --rm \
  -e QT_QPA_PLATFORM=wayland \
  -e XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR} \
  -e WAYLAND_DISPLAY=${WAYLAND_DISPLAY} \
  -v ${XDG_RUNTIME_DIR}:${XDG_RUNTIME_DIR} \
  --user $(id -u):$(id -g) \
  --net=host \
  --device /dev/dri \
  --security-opt seccomp=unconfined \
  --security-opt apparmor=unconfined \
  --ipc=host \
  timojj/raster-algorithms-lab
