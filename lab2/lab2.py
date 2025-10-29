import sys
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QTableWidget, 
                               QTableWidgetItem, QPushButton, QFileDialog, 
                               QLabel, QProgressBar, QLineEdit, QMessageBox,
                               QHeaderView, QTabWidget, QTextEdit, QSplitter,
                               QGroupBox, QFrame, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter
import PIL.Image
from PIL.ExifTags import TAGS
import PIL.ExifTags

class ImageInfo:
    def __init__(self):
        self.filename = ""
        self.filepath = ""
        self.size = "Н/Д"
        self.resolution = "Н/Д"
        self.color_depth = "Н/Д"
        self.compression = "Н/Д"
        self.format = "Н/Д"
        self.mode = "Н/Д"
        self.extra_info = ""
        self.error = ""

class ImageInfoWorker(QThread):
    progress = Signal(int)
    file_processed = Signal(str, ImageInfo)
    finished = Signal()
    
    def __init__(self, folder_path, single_file_mode=False, single_file_path=""):
        super().__init__()
        self.folder_path = folder_path
        self.single_file_mode = single_file_mode
        self.single_file_path = single_file_path
        self.image_files = []
        self.stop_requested = False
        
    def get_supported_formats(self):
        return {'.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.bmp', '.png', '.pcx'}
    
    def find_image_files(self):
        if self.single_file_mode:
            if os.path.exists(self.single_file_path):
                return [self.single_file_path]
            else:
                return []
                
        if not os.path.exists(self.folder_path):
            return []
            
        image_files = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if Path(file).suffix.lower() in self.get_supported_formats():
                    image_files.append(os.path.join(root, file))
                if len(image_files) >= 100000:
                    break
            if len(image_files) >= 100000:
                break
        return image_files
    
    def get_resolution_dpi(self, image):
        try:
            dpi = image.info.get('dpi', (72, 72))
            if dpi and dpi[0] > 0:
                return f"{dpi[0]} × {dpi[1]} dpi"
        except:
            pass
        return "Н/Д"
    
    def get_compression_info(self, image, format):
        try:
            if format.upper() in ['JPEG', 'JPG']:
                return "JPEG сжатие"
            elif format.upper() == 'TIFF':
                compression = image.info.get('compression', 'Н/Д')
                compression_names = {
                    1: 'Без сжатия',
                    5: 'LZW',
                    6: 'JPEG',
                    7: 'JPEG',
                    8: 'Deflate'
                }
                return compression_names.get(compression, f'Неизвестно ({compression})')
            elif format.upper() == 'PNG':
                return 'Deflate'
            elif format.upper() == 'GIF':
                return 'LZW'
            elif format.upper() == 'BMP':
                return 'Без сжатия'
            elif format.upper() == 'PCX':
                return 'RLE'
        except:
            pass
        return "Н/Д"
    
    def get_color_depth(self, image):
        try:
            if hasattr(image, 'bits'):
                return f"{image.bits} бит"
            else:
                mode_bits = {
                    '1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32,
                    'CMYK': 32, 'YCbCr': 24, 'LAB': 24, 'HSV': 24
                }
                bits = mode_bits.get(image.mode, len(image.getbands()) * 8)
                return f"{bits} бит"
        except:
            return "Н/Д"
    
    def get_extra_info(self, image, format):
        extra_info = []
        
        try:
            if format.upper() in ['JPEG', 'JPG', 'TIFF', 'TIF']:
                exif_data = image._getexif()
                if exif_data:
                    extra_info.append("=== EXIF ДАННЫЕ ===")
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename']:
                            extra_info.append(f"{tag}: {value}")
            
            if format.upper() == 'GIF' and image.mode == 'P':
                colors = image.getcolors()
                if colors:
                    extra_info.append("=== ИНФОРМАЦИЯ О ПАЛИТРЕ ===")
                    extra_info.append(f"Количество цветов: {len(colors)}")
            
            extra_info.append("=== ОСНОВНАЯ ИНФОРМАЦИЯ ===")
            extra_info.append(f"Цветовой режим: {image.mode}")
            extra_info.append(f"Количество каналов: {len(image.getbands())}")
            
            if hasattr(image, 'has_transparency') and image.has_transparency:
                extra_info.append("Прозрачность: Да")
            
            # Размер файла
            if hasattr(image, 'fp') and hasattr(image.fp, 'name'):
                file_size = os.path.getsize(image.fp.name)
                extra_info.append(f"Размер файла: {file_size / 1024:.1f} КБ")
            
        except Exception as e:
            extra_info.append(f"Ошибка получения доп. информации: {str(e)}")
        
        return "\n".join(extra_info) if extra_info else "Дополнительная информация отсутствует"
    
    def get_image_info(self, filepath):
        info = ImageInfo()
        info.filepath = filepath
        info.filename = os.path.basename(filepath)
        
        try:
            with PIL.Image.open(filepath) as img:
                # Основная информация
                info.size = f"{img.width} × {img.height}"
                info.resolution = self.get_resolution_dpi(img)
                info.color_depth = self.get_color_depth(img)
                info.format = img.format
                info.mode = img.mode
                info.compression = self.get_compression_info(img, img.format)
                info.extra_info = self.get_extra_info(img, img.format)
                
        except Exception as e:
            info.error = f"Ошибка: {str(e)}"
        
        return info
    
    def run(self):
        self.image_files = self.find_image_files()
        total_files = len(self.image_files)
        
        if total_files == 0:
            self.finished.emit()
            return
        
        if self.single_file_mode and total_files == 1:
            try:
                info = self.get_image_info(self.image_files[0])
                self.file_processed.emit(self.image_files[0], info)
                self.progress.emit(100)
            except Exception as e:
                info = ImageInfo()
                info.filepath = self.image_files[0]
                info.filename = os.path.basename(self.image_files[0])
                info.error = f"Ошибка обработки: {str(e)}"
                self.file_processed.emit(self.image_files[0], info)
        else:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i, filepath in enumerate(self.image_files):
                    if self.stop_requested:
                        break
                    future = executor.submit(self.get_image_info, filepath)
                    futures.append((filepath, future))
                    
                for i, (filepath, future) in enumerate(futures):
                    if self.stop_requested:
                        break
                    try:
                        info = future.result(timeout=10)
                        self.file_processed.emit(filepath, info)
                        progress = int((i + 1) / total_files * 100)
                        self.progress.emit(progress)
                    except Exception as e:
                        info = ImageInfo()
                        info.filepath = filepath
                        info.filename = os.path.basename(filepath)
                        info.error = f"Ошибка обработки: {str(e)}"
                        self.file_processed.emit(filepath, info)
        
        self.finished.emit()
    
    def stop(self):
        self.stop_requested = True

class StyledTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setup_table()
        
    def setup_table(self):
        headers = [
            "Имя файла", "Размер (пикс.)", "Разрешение", "Глубина цвета", 
            "Сжатие", "Формат", "Режим", "Статус"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Настройка внешнего вида
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 1px solid #ced4da;
                border-radius: 5px;
                color: #212529;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #dee2e6;
                color: #212529;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                padding: 8px;
                border: 1px solid #495057;
                font-weight: bold;
            }
        """)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSortingEnabled(True)
        self.setShowGrid(True)
        
        self.setColumnWidth(0, 250)  # Имя файла
        self.setColumnWidth(1, 120)  # Размер
        self.setColumnWidth(2, 130)  # Разрешение
        self.setColumnWidth(3, 110)  # Глубина цвета
        self.setColumnWidth(4, 120)  # Сжатие
        self.setColumnWidth(5, 80)   # Формат
        self.setColumnWidth(6, 80)   # Режим
        self.setColumnWidth(7, 150)  # Статус
        
        self.setMinimumHeight(400)
    
    def add_image_info(self, info):
        """Добавляет информацию об изображении в таблицу"""
        row = self.rowCount()
        self.insertRow(row)
        
        items = [
            info.filename,
            info.size,
            info.resolution,
            info.color_depth,
            info.compression,
            info.format,
            info.mode,
            "✓ Успешно" if not info.error else f"✗ {info.error}"
        ]
        
        for col, text in enumerate(items):
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            
            if info.error:
                if col == 7:
                    item.setForeground(QColor(220, 53, 69))
                    item.setBackground(QColor(255, 240, 240))
            else:
                if col == 7:
                    item.setForeground(QColor(40, 167, 69))
                    item.setBackground(QColor(240, 255, 240))
            
            if col in [1, 2, 3, 5, 6]:
                item.setTextAlignment(Qt.AlignCenter)
                
            self.setItem(row, col, item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.image_info_dict = {}
        self.scan_mode = "folder"  # "folder" или "file"
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Анализатор графических файлов - Лабораторная работа №2")
        self.setGeometry(100, 100, 1400, 800)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QPushButton#stopBtn {
                background-color: #dc3545;
            }
            QPushButton#stopBtn:hover {
                background-color: #c82333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                color: #212529;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ced4da;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #212529;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #212529;
            }
            QProgressBar {
                border: 2px solid #ced4da;
                border-radius: 5px;
                text-align: center;
                background-color: #e9ecef;
                color: #212529;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                width: 20px;
            }
            QTabWidget::pane {
                border: 1px solid #ced4da;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #212529;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
                color: #212529;
            }
            QLabel {
                color: #212529;
            }
            QTextEdit {
                color: #212529;
            }
            QRadioButton {
                color: #212529;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                background-color: #007bff;
                border: 2px solid #0056b3;
                border-radius: 7px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("Анализатор графических файлов")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #212529;
                padding: 10px;
                background-color: #e9ecef;
                border-radius: 5px;
                text-align: center;
                border: 2px solid #ced4da;
            }
        """)
        layout.addWidget(title_label)
        
        mode_group = QGroupBox("Режим сканирования")
        mode_layout = QHBoxLayout(mode_group)
        
        self.folder_radio = QRadioButton("Сканировать папку")
        self.file_radio = QRadioButton("Анализировать один файл")
        self.folder_radio.setChecked(True)
        
        self.mode_button_group = QButtonGroup()
        self.mode_button_group.addButton(self.folder_radio)
        self.mode_button_group.addButton(self.file_radio)
        self.mode_button_group.buttonClicked.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.folder_radio)
        mode_layout.addWidget(self.file_radio)
        mode_layout.addStretch()
        
        layout.addWidget(mode_group)
        
        control_group = QGroupBox("Управление сканированием")
        control_layout = QVBoxLayout(control_group)
        
        path_layout = QHBoxLayout()
        
        self.path_label = QLabel("Папка:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Выберите папку с графическими файлами...")
        
        self.browse_btn = QPushButton("Обзор")
        self.browse_btn.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_input, 1)
        path_layout.addWidget(self.browse_btn)
        
        buttons_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("Начать сканирование")
        self.scan_btn.clicked.connect(self.start_scanning)
        self.scan_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_scanning)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setObjectName("stopBtn")
        
        buttons_layout.addWidget(self.scan_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addStretch()
        
        control_layout.addLayout(path_layout)
        control_layout.addLayout(buttons_layout)
        layout.addWidget(control_group)

        self.progress_label = QLabel("Готов к работе")
        self.progress_label.setStyleSheet("font-weight: bold; color: #6c757d;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        self.tabs = QTabWidget()
        
        self.table_widget = StyledTableWidget()
        self.tabs.addTab(self.table_widget, "Основная информация")
        
        self.extra_info_text = QTextEdit()
        self.extra_info_text.setReadOnly(True)
        self.extra_info_text.setPlaceholderText("Выберите изображение для просмотра дополнительной информации...")
        self.extra_info_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                color: #212529;
            }
        """)
        self.tabs.addTab(self.extra_info_text, "Детальная информация")
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 5px;
                padding: 10px;
                font-family: Arial;
                color: #212529;
            }
        """)
        self.tabs.addTab(self.stats_text, "Статистика")
        
        layout.addWidget(self.tabs, 1)
        
        self.table_widget.itemSelectionChanged.connect(self.show_extra_info)
        
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")
        self.update_stats()
    
    def on_mode_changed(self):
        if self.folder_radio.isChecked():
            self.scan_mode = "folder"
            self.path_label.setText("Папка:")
            self.path_input.setPlaceholderText("Выберите папку с графическими файлами...")
            self.scan_btn.setText("Начать сканирование")
        else:
            self.scan_mode = "file"
            self.path_label.setText("Файл:")
            self.path_input.setPlaceholderText("Выберите графический файл...")
            self.scan_btn.setText("Анализировать файл")
        
        self.path_input.clear()
        self.scan_btn.setEnabled(False)
    
    def browse_path(self):
        if self.scan_mode == "folder":
            path = QFileDialog.getExistingDirectory(self, "Выберите папку с изображениями")
            if path:
                self.path_input.setText(path)
                self.scan_btn.setEnabled(True)
                
                supported_formats = {'.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.bmp', '.png', '.pcx'}
                image_count = sum(1 for f in Path(path).rglob('*') 
                                if f.suffix.lower() in supported_formats)
                self.status_bar.showMessage(f"Найдено {image_count} поддерживаемых графических файлов")
        else:
            file_filter = "Графические файлы (*.jpg *.jpeg *.png *.gif *.bmp *.tif *.tiff *.pcx);;Все файлы (*)"
            file_path, _ = QFileDialog.getOpenFileName(self, "Выберите графический файл", "", file_filter)
            if file_path:
                self.path_input.setText(file_path)
                self.scan_btn.setEnabled(True)
                file_ext = Path(file_path).suffix.lower()
                supported_formats = {'.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.bmp', '.png', '.pcx'}
                if file_ext in supported_formats:
                    self.status_bar.showMessage(f"Выбран файл: {os.path.basename(file_path)}")
                else:
                    self.status_bar.showMessage(f"Внимание: выбранный файл может не поддерживаться")
    
    def start_scanning(self):
        path = self.path_input.text()
        if not path:
            QMessageBox.warning(self, "Ошибка", "Путь не выбран!")
            return
        
        if not os.path.exists(path):
            QMessageBox.warning(self, "Ошибка", "Выбранный путь не существует!")
            return
        
        self.table_widget.setRowCount(0)
        self.extra_info_text.clear()
        self.image_info_dict = {}
        
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if self.scan_mode == "folder":
            self.progress_label.setText("Сканирование изображений...")
        else:
            self.progress_label.setText("Анализ файла...")
            
        self.progress_label.setStyleSheet("font-weight: bold; color: #007bff;")

        if self.scan_mode == "folder":
            self.worker = ImageInfoWorker(path)
        else:
            self.worker = ImageInfoWorker("", single_file_mode=True, single_file_path=path)
            
        self.worker.file_processed.connect(self.on_file_processed)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()
    
    def stop_scanning(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)
        self.on_scan_finished()
    
    def on_file_processed(self, filepath, info):
        self.image_info_dict[filepath] = info
        self.table_widget.add_image_info(info)
    
    def on_progress(self, value):
        self.progress_bar.setValue(value)
        if self.scan_mode == "folder":
            self.progress_label.setText(f"Сканирование... {value}% завершено")
        else:
            self.progress_label.setText(f"Анализ файла... {value}% завершено")
    
    def on_scan_finished(self):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if self.scan_mode == "folder":
            self.progress_label.setText(f"Сканирование завершено. Обработано {self.table_widget.rowCount()} файлов.")
        else:
            self.progress_label.setText("Анализ файла завершен.")
            
        self.progress_label.setStyleSheet("font-weight: bold; color: #28a745;")
        
        self.update_stats()
    
    def show_extra_info(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        filename_item = self.table_widget.item(row, 0)
        if not filename_item:
            return
            
        filename = filename_item.text()
        
        for filepath, info in self.image_info_dict.items():
            if info.filename == filename:
                extra_text = f"ФАЙЛ: {info.filename}\n"
                extra_text += f"ПУТЬ: {info.filepath}\n"
                extra_text += "="*50 + "\n\n"
                extra_text += f"РАЗМЕР: {info.size} пикселей\n"
                extra_text += f"РАЗРЕШЕНИЕ: {info.resolution}\n"
                extra_text += f"ГЛУБИНА ЦВЕТА: {info.color_depth}\n"
                extra_text += f"СЖАТИЕ: {info.compression}\n"
                extra_text += f"ФОРМАТ: {info.format}\n"
                extra_text += f"РЕЖИМ: {info.mode}\n\n"
                
                if info.extra_info:
                    extra_text += "ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:\n" + "="*30 + "\n"
                    extra_text += info.extra_info
                else:
                    extra_text += "Дополнительная информация отсутствует."
                
                self.extra_info_text.setText(extra_text)
                break
    
    def update_stats(self):
        total_files = self.table_widget.rowCount()
        if total_files == 0:
            self.stats_text.setText("Файлы еще не обработаны.")
            return
        
        # Подсчет по форматам
        format_count = {}
        for row in range(total_files):
            format_item = self.table_widget.item(row, 5)
            if format_item:
                format_name = format_item.text()
                format_count[format_name] = format_count.get(format_name, 0) + 1
        
        stats_text = "СТАТИСТИКА ОБРАБОТКИ\n"
        stats_text += "="*30 + "\n\n"
        
        if self.scan_mode == "folder":
            stats_text += f"Всего обработано файлов: {total_files}\n\n"
        else:
            stats_text += "Режим: анализ одного файла\n\n"
        
        stats_text += "Распределение по форматам:\n"
        stats_text += "-"*25 + "\n"
        for format_name, count in sorted(format_count.items()):
            if self.scan_mode == "folder":
                percentage = (count / total_files) * 100
                stats_text += f"  {format_name}: {count} файлов ({percentage:.1f}%)\n"
            else:
                stats_text += f"  {format_name}: 1 файл\n"
        
        error_count = sum(1 for row in range(total_files) 
                         if self.table_widget.item(row, 7) and 
                         "✗" in self.table_widget.item(row, 7).text())
        
        if self.scan_mode == "folder":
            stats_text += f"\nФайлов с ошибками: {error_count}\n"
            stats_text += f"Успешно обработано: {total_files - error_count}\n"
            success_rate = ((total_files - error_count) / total_files * 100)
            stats_text += f"Процент успеха: {success_rate:.1f}%\n"
        else:
            if error_count == 0:
                stats_text += f"\nСтатус: ✓ Успешно обработан\n"
            else:
                stats_text += f"\nСтатус: ✗ Ошибка обработки\n"
        
        stats_text += "\nПОДДЕРЖИВАЕМЫЕ ФОРМАТЫ:\n"
        stats_text += "-"*25 + "\n"
        stats_text += "• JPEG/JPG - Формат сжатия с потерями\n"
        stats_text += "• PNG - Сжатие без потерь с прозрачностью\n"
        stats_text += "• GIF - Анимация и палитра цветов\n"
        stats_text += "• BMP - Формат без сжатия\n"
        stats_text += "• TIFF - Высококачественные изображения\n"
        stats_text += "• PCX - Формат Paintbrush\n"
        
        self.stats_text.setText(stats_text)
        
        if self.scan_mode == "folder":
            self.status_bar.showMessage(f"Обработано {total_files} файлов, {error_count} ошибок")
        else:
            if error_count == 0:
                self.status_bar.showMessage("Файл успешно проанализирован")
            else:
                self.status_bar.showMessage("Ошибка при анализе файла")

def main():
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()