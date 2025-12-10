import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QSlider, 
                               QComboBox, QGroupBox, QFileDialog, QMessageBox,
                               QSplitter, QScrollArea, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QAction


class ImageProcessor:
    @staticmethod
    def read_image(file_path):
        """Чтение изображения из файлa"""
        try:
            from PIL import Image
            img = Image.open(file_path)
            img_array = np.array(img)
            
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]
                    img_array = img_array[:, :, ::-1]
                elif img_array.shape[2] == 3:
                    img_array = img_array[:, :, ::-1]
            
            return img_array
        except ImportError:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if file_path.lower().endswith('.png'):
                return ImageProcessor._read_png_simple(data)
            elif file_path.lower().endswith(('.jpg', '.jpeg')):
                return ImageProcessor._read_jpeg_simple(data)
            else:
                raise ValueError(f"Unsupported image format: {file_path}")
    
    @staticmethod
    def _read_png_simple(data):
        return np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    @staticmethod
    def _read_jpeg_simple(data):
        return np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    @staticmethod
    def save_image(file_path, image):
        """Сохранение изображения в файл"""
        try:
            from PIL import Image
            
            if len(image.shape) == 3:
                rgb_image = image[:, :, ::-1].copy()
                img = Image.fromarray(rgb_image)
            else:
                img = Image.fromarray(image)
            
            img.save(file_path)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def convert_color(image, conversion):
        """Конвертация цветового пространства"""
        if len(image.shape) != 3:
            return image
        
        if conversion == "BGR2GRAY":
            if image.shape[2] == 3:
                gray = (
                    0.299 * image[:, :, 2] +
                    0.587 * image[:, :, 1] +
                    0.114 * image[:, :, 0]
                ).astype(np.uint8)
                return gray
            else:
                return image[:, :, 0]
        
        elif conversion == "GRAY2BGR":
            if len(image.shape) == 2:
                h, w = image.shape
                bgr = np.zeros((h, w, 3), dtype=np.uint8)
                bgr[:, :, 0] = image
                bgr[:, :, 1] = image
                bgr[:, :, 2] = image
                return bgr
        
        return image
    
    @staticmethod
    def resize_image(image, new_size):
        """Изменение размера изображения"""
        h, w = image.shape[:2]
        new_h, new_w = new_size
        
        if len(image.shape) == 3:
            resized = np.zeros((new_h, new_w, image.shape[2]), dtype=image.dtype)
            for y in range(new_h):
                for x in range(new_w):
                    src_y = y * (h - 1) / (new_h - 1) if new_h > 1 else 0
                    src_x = x * (w - 1) / (new_w - 1) if new_w > 1 else 0
                    
                    y1 = int(src_y)
                    x1 = int(src_x)
                    
                    dy = src_y - y1
                    dx = src_x - x1
                    
                    y1 = min(y1, h - 1)
                    x1 = min(x1, w - 1)
                    y2 = min(y1 + 1, h - 1)
                    x2 = min(x1 + 1, w - 1)
                    
                    for c in range(image.shape[2]):
                        value = (image[y1, x1, c] * (1 - dx) * (1 - dy) +
                                image[y1, x2, c] * dx * (1 - dy) +
                                image[y2, x1, c] * (1 - dx) * dy +
                                image[y2, x2, c] * dx * dy)
                        resized[y, x, c] = int(np.clip(value, 0, 255))
        else:
            resized = np.zeros((new_h, new_w), dtype=image.dtype)
            for y in range(new_h):
                for x in range(new_w):
                    src_y = y * (h - 1) / (new_h - 1) if new_h > 1 else 0
                    src_x = x * (w - 1) / (new_w - 1) if new_w > 1 else 0
                    
                    y1 = int(src_y)
                    x1 = int(src_x)
                    
                    dy = src_y - y1
                    dx = src_x - x1
                    
                    y1 = min(y1, h - 1)
                    x1 = min(x1, w - 1)
                    y2 = min(y1 + 1, h - 1)
                    x2 = min(x1 + 1, w - 1)
                    
                    value = (image[y1, x1] * (1 - dx) * (1 - dy) +
                            image[y1, x2] * dx * (1 - dy) +
                            image[y2, x1] * (1 - dx) * dy +
                            image[y2, x2] * dx * dy)
                    resized[y, x] = int(np.clip(value, 0, 255))
        
        return resized
    
    @staticmethod
    def global_threshold_otsu(image):
        """Реализация метода Оцу"""
        if len(image.shape) == 3:
            gray = ImageProcessor.convert_color(image, "BGR2GRAY")
        else:
            gray = image.copy()
        
        histogram = np.zeros(256, dtype=np.float32)
        total_pixels = gray.size
        
        for i in range(gray.shape[0]):
            for j in range(gray.shape[1]):
                histogram[gray[i, j]] += 1
        
        histogram /= total_pixels
        
        best_threshold = 0
        best_variance = 0.0
        
        for threshold in range(1, 256):
            w0 = np.sum(histogram[:threshold])
            w1 = np.sum(histogram[threshold:])
            
            if w0 < 1e-10 or w1 < 1e-10:
                continue
            
            mean0 = np.sum(np.arange(threshold) * histogram[:threshold]) / w0
            mean1 = np.sum(np.arange(threshold, 256) * histogram[threshold:]) / w1
            
            variance = w0 * w1 * (mean0 - mean1) ** 2
            
            if variance > best_variance:
                best_variance = variance
                best_threshold = threshold
        
        result = np.zeros_like(gray)
        result[gray > best_threshold] = 255
        
        return result
    
    @staticmethod
    def global_threshold_iterative(image, max_iterations=100, tolerance=1, progress_callback=None):
        """Итеративный метод пороговой обработки"""
        if len(image.shape) == 3:
            gray = ImageProcessor.convert_color(image, "BGR2GRAY")
        else:
            gray = image.copy()
        
        threshold = np.mean(gray)
        
        for i in range(max_iterations):
            if progress_callback:
                progress_callback(int((i / max_iterations) * 100))
            
            foreground = gray[gray > threshold]
            background = gray[gray <= threshold]
            
            if foreground.size == 0 or background.size == 0:
                break
            
            mean_foreground = np.mean(foreground)
            mean_background = np.mean(background)
            
            new_threshold = (mean_foreground + mean_background) / 2
            
            if abs(new_threshold - threshold) < tolerance:
                break
                
            threshold = new_threshold
        
        result = np.zeros_like(gray)
        result[gray > threshold] = 255
        
        return result, threshold
    
    @staticmethod
    def global_threshold_manual(image, threshold_value):
        """Ручная пороговая обработка"""
        if len(image.shape) == 3:
            gray = ImageProcessor.convert_color(image, "BGR2GRAY")
        else:
            gray = image.copy()
        
        result = np.zeros_like(gray)
        result[gray > threshold_value] = 255
        
        return result
    
    @staticmethod
    def adaptive_threshold_mean(image, block_size=11, C=2):
        """Адаптивная пороговая обработка по среднему"""
        if len(image.shape) == 3:
            gray = ImageProcessor.convert_color(image, "BGR2GRAY")
        else:
            gray = image.copy()
        
        if block_size % 2 == 0:
            block_size += 1
        
        height, width = gray.shape
        half_block = block_size // 2
        
        result = np.zeros_like(gray)
        
        padded = np.zeros((height + 2 * half_block, width + 2 * half_block), dtype=gray.dtype)
        
        padded[half_block:half_block+height, half_block:half_block+width] = gray
        
        for i in range(half_block):
            padded[i, half_block:half_block+width] = gray[half_block-i, :]
        
        for i in range(half_block):
            padded[height+half_block+i, half_block:half_block+width] = gray[height-2-i, :]
        
        for i in range(half_block):
            padded[:, i] = padded[:, 2*half_block - i]
        
        for i in range(half_block):
            padded[:, width+half_block+i] = padded[:, width+half_block-i-2]
        
        for y in range(height):
            for x in range(width):
                window = padded[y:y+block_size, x:x+block_size]
                
                mean_value = np.mean(window)
                
                if gray[y, x] > (mean_value - C):
                    result[y, x] = 255
        
        return result
    
    @staticmethod
    def sharpen_filter_laplacian(image, strength=1.0):
        """Фильтр Лапласа"""
        strength = float(np.clip(strength, 0.01, 1.0))
        
        base_kernel = np.array([[0, -1, 0],
                                [-1, 5, -1],
                                [0, -1, 0]], dtype=np.float32)
        
        identity_kernel = np.array([[0, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 0]], dtype=np.float32)
        
        kernel = (1.0 - strength) * identity_kernel + strength * base_kernel
        
        if len(image.shape) == 3:
            h, w, ch = image.shape
            
            padded = np.zeros((h + 2, w + 2, ch), dtype=np.float32)
            padded[1:-1, 1:-1, :] = image.astype(np.float32)
            
            padded[0, 1:-1, :] = image[1, :, :]
            padded[-1, 1:-1, :] = image[-2, :, :]
            padded[1:-1, 0, :] = image[:, 1, :]
            padded[1:-1, -1, :] = image[:, -2, :]
            padded[0, 0, :] = image[1, 1, :]
            padded[0, -1, :] = image[1, -2, :]
            padded[-1, 0, :] = image[-2, 1, :]
            padded[-1, -1, :] = image[-2, -2, :]
            
            dst = np.zeros((h, w, ch), dtype=np.float32)
            
            for c in range(ch):
                channel = padded[:, :, c]
                dst[:, :, c] = (
                    kernel[0, 0] * channel[0:-2, 0:-2] +
                    kernel[0, 1] * channel[0:-2, 1:-1] +
                    kernel[0, 2] * channel[0:-2, 2:] +
                    kernel[1, 0] * channel[1:-1, 0:-2] +
                    kernel[1, 1] * channel[1:-1, 1:-1] +
                    kernel[1, 2] * channel[1:-1, 2:] +
                    kernel[2, 0] * channel[2:, 0:-2] +
                    kernel[2, 1] * channel[2:, 1:-1] +
                    kernel[2, 2] * channel[2:, 2:]
                )
            
            dst = np.clip(dst, 0, 255).astype(np.uint8)
            return dst
        else:
            h, w = image.shape
            gray = image.astype(np.float32)
            
            padded = np.zeros((h + 2, w + 2), dtype=np.float32)
            padded[1:-1, 1:-1] = gray
            
            padded[0, 1:-1] = gray[1, :]
            padded[-1, 1:-1] = gray[-2, :]
            padded[1:-1, 0] = gray[:, 1]
            padded[1:-1, -1] = gray[:, -2]
            padded[0, 0] = gray[1, 1]
            padded[0, -1] = gray[1, -2]
            padded[-1, 0] = gray[-2, 1]
            padded[-1, -1] = gray[-2, -2]
            
            dst = (
                kernel[0, 0] * padded[0:-2, 0:-2] +
                kernel[0, 1] * padded[0:-2, 1:-1] +
                kernel[0, 2] * padded[0:-2, 2:] +
                kernel[1, 0] * padded[1:-1, 0:-2] +
                kernel[1, 1] * padded[1:-1, 1:-1] +
                kernel[1, 2] * padded[1:-1, 2:] +
                kernel[2, 0] * padded[2:, 0:-2] +
                kernel[2, 1] * padded[2:, 1:-1] +
                kernel[2, 2] * padded[2:, 2:]
            )
            
            dst = np.clip(dst, 0, 255).astype(np.uint8)
            return dst


class ProcessingThread(QThread):
    finished = Signal(object)
    progress = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.method = None
        self.image = None
        self.params = {}
        
    def run(self):
        try:
            if self.method == "global_otsu":
                result = ImageProcessor.global_threshold_otsu(self.image)
            elif self.method == "global_iterative":
                result, threshold = ImageProcessor.global_threshold_iterative(
                    self.image, 
                    progress_callback=lambda p: self.progress.emit(p)
                )
            elif self.method == "global_manual":
                result = ImageProcessor.global_threshold_manual(
                    self.image, 
                    self.params.get('threshold', 127)
                )
            elif self.method == "adaptive_mean":
                result = ImageProcessor.adaptive_threshold_mean(
                    self.image,
                    self.params.get('block_size', 11),
                    self.params.get('C', 2)
                )
            elif self.method == "sharpen_laplacian":
                result = ImageProcessor.sharpen_filter_laplacian(
                    self.image,
                    self.params.get('strength', 0.2)
                )
            else:
                result = None
                
            self.finished.emit(result)
        except Exception as e:
            print(f"Error in processing thread: {e}")
            self.finished.emit(None)


class ImageViewer(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.setText("Загрузите изображение")
        self.setMinimumSize(400, 300)


class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.processed_image = None
        self.processing_thread = ProcessingThread()
        self.progress_dialog = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Обработка изображений - Пороговая обработка и увеличение резкости")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        
        self.original_scroll = QScrollArea()
        self.original_viewer = ImageViewer()
        self.original_scroll.setWidget(self.original_viewer)
        self.original_scroll.setWidgetResizable(True)
        
        self.processed_scroll = QScrollArea()
        self.processed_viewer = ImageViewer()
        self.processed_scroll.setWidget(self.processed_viewer)
        self.processed_scroll.setWidgetResizable(True)
        
        image_layout.addWidget(QLabel("Оригинальное изображение:"))
        image_layout.addWidget(self.original_scroll)
        image_layout.addWidget(QLabel("Обработанное изображение:"))
        image_layout.addWidget(self.processed_scroll)
        
        control_panel = self.create_control_panel()
        
        splitter.addWidget(image_widget)
        splitter.addWidget(control_panel)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        self.create_menu()
        self.connect_thread_signals()
    
    def connect_thread_signals(self):
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.progress.connect(self.on_processing_progress)
    
    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        global_group = QGroupBox("Глобальная пороговая обработка")
        global_layout = QVBoxLayout(global_group)
        
        self.global_method_combo = QComboBox()
        self.global_method_combo.addItems(["Метод Оцу", "Итеративный метод", "Ручной метод"])
        global_layout.addWidget(QLabel("Метод:"))
        global_layout.addWidget(self.global_method_combo)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(127)
        self.threshold_slider.setEnabled(False)
        global_layout.addWidget(QLabel("Пороговое значение:"))
        global_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("127")
        global_layout.addWidget(self.threshold_label)
        
        self.apply_global_btn = QPushButton("Применить глобальную пороговую обработку")
        global_layout.addWidget(self.apply_global_btn)
        
        layout.addWidget(global_group)
        
        adaptive_group = QGroupBox("Адаптивная пороговая обработка")
        adaptive_layout = QVBoxLayout(adaptive_group)
        
        adaptive_layout.addWidget(QLabel("Метод: По локальному среднему"))
        
        self.block_size_slider = QSlider(Qt.Horizontal)
        self.block_size_slider.setRange(3, 31)
        self.block_size_slider.setValue(11)
        adaptive_layout.addWidget(QLabel("Размер блока (нечетный):"))
        adaptive_layout.addWidget(self.block_size_slider)
        self.block_size_label = QLabel("11")
        adaptive_layout.addWidget(self.block_size_label)
        
        self.c_slider = QSlider(Qt.Horizontal)
        self.c_slider.setRange(0, 20)
        self.c_slider.setValue(2)
        adaptive_layout.addWidget(QLabel("Константа C:"))
        adaptive_layout.addWidget(self.c_slider)
        self.c_label = QLabel("2")
        adaptive_layout.addWidget(self.c_label)
        
        self.apply_adaptive_btn = QPushButton("Применить адаптивную пороговую обработку")
        adaptive_layout.addWidget(self.apply_adaptive_btn)
        
        layout.addWidget(adaptive_group)
        
        sharpen_group = QGroupBox("Увеличение резкости")
        sharpen_layout = QVBoxLayout(sharpen_group)
        
        sharpen_layout.addWidget(QLabel("Метод: Лапласиан"))
        
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(1, 100)
        self.strength_slider.setValue(20)
        sharpen_layout.addWidget(QLabel("Сила увеличения резкости:"))
        sharpen_layout.addWidget(self.strength_slider)
        self.strength_label = QLabel("0.2")
        sharpen_layout.addWidget(self.strength_label)
        
        self.apply_sharpen_btn = QPushButton("Применить увеличение резкости")
        sharpen_layout.addWidget(self.apply_sharpen_btn)
        
        layout.addWidget(sharpen_group)
        
        self.reset_btn = QPushButton("Сбросить изображение")
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()
        
        self.connect_signals()
        
        return panel
    
    def connect_signals(self):
        self.global_method_combo.currentTextChanged.connect(self.on_global_method_changed)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        self.block_size_slider.valueChanged.connect(self.on_block_size_changed)
        self.c_slider.valueChanged.connect(self.on_c_changed)
        self.strength_slider.valueChanged.connect(self.on_strength_changed)
        
        self.apply_global_btn.clicked.connect(self.apply_global_threshold)
        self.apply_adaptive_btn.clicked.connect(self.apply_adaptive_threshold)
        self.apply_sharpen_btn.clicked.connect(self.apply_sharpen)
        self.reset_btn.clicked.connect(self.reset_image)
    
    def create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Файл')
        
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_image)
        
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_image)
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
    
    def on_global_method_changed(self, method):
        if method == "Ручной метод":
            self.threshold_slider.setEnabled(True)
        else:
            self.threshold_slider.setEnabled(False)
    
    def on_threshold_changed(self, value):
        self.threshold_label.setText(str(value))
    
    def on_block_size_changed(self, value):
        if value % 2 == 0:
            value += 1
            self.block_size_slider.setValue(value)
        self.block_size_label.setText(str(value))
    
    def on_c_changed(self, value):
        self.c_label.setText(str(value))
    
    def on_strength_changed(self, value):
        strength = value / 100.0
        self.strength_label.setText(f"{strength:.2f}")
    
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            try:
                self.original_image = ImageProcessor.read_image(file_path)
                if self.original_image is not None:
                    h, w = self.original_image.shape[:2]
                    if h > 1024 or w > 1024:
                        scale = min(1024/h, 1024/w)
                        new_h, new_w = int(h * scale), int(w * scale)
                        self.original_image = ImageProcessor.resize_image(
                            self.original_image, (new_h, new_w)
                        )
                    
                    self.processed_image = self.original_image.copy()
                    self.display_images()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки изображения: {str(e)}")
    
    def save_image(self):
        if self.processed_image is None:
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "", 
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        
        if file_path:
            try:
                success = ImageProcessor.save_image(file_path, self.processed_image)
                if success:
                    QMessageBox.information(self, "Успех", "Изображение сохранено")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изображение")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def display_images(self):
        if self.original_image is not None:
            if len(self.original_image.shape) == 3:
                original_rgb = self.original_image[:, :, ::-1].copy()
                original_qimage = QImage(
                    original_rgb.data, 
                    original_rgb.shape[1], 
                    original_rgb.shape[0], 
                    original_rgb.strides[0], 
                    QImage.Format_RGB888
                )
            else:
                original_qimage = QImage(
                    self.original_image.data,
                    self.original_image.shape[1],
                    self.original_image.shape[0],
                    self.original_image.strides[0],
                    QImage.Format_Grayscale8
                )
            self.original_viewer.setPixmap(QPixmap.fromImage(original_qimage))
        
        if self.processed_image is not None:
            if len(self.processed_image.shape) == 2:
                processed_qimage = QImage(
                    self.processed_image.data,
                    self.processed_image.shape[1],
                    self.processed_image.shape[0],
                    self.processed_image.strides[0],
                    QImage.Format_Grayscale8
                )
            else:
                processed_rgb = self.processed_image[:, :, ::-1].copy()
                processed_qimage = QImage(
                    processed_rgb.data,
                    processed_rgb.shape[1],
                    processed_rgb.shape[0],
                    processed_rgb.strides[0],
                    QImage.Format_RGB888
                )
            self.processed_viewer.setPixmap(QPixmap.fromImage(processed_qimage))
    
    def show_progress_dialog(self, title="Обработка..."):
        self.progress_dialog = QProgressDialog(title, "Отмена", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
    
    def on_processing_progress(self, value):
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
    
    def on_processing_finished(self, result):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if result is not None:
            self.processed_image = result
            self.display_images()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обработать изображение")
    
    def apply_global_threshold(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        method = self.global_method_combo.currentText()
        
        self.processing_thread.method = {
            "Метод Оцу": "global_otsu",
            "Итеративный метод": "global_iterative",
            "Ручной метод": "global_manual"
        }[method]
        
        self.processing_thread.image = self.original_image.copy()
        
        if method == "Ручной метод":
            self.processing_thread.params = {'threshold': self.threshold_slider.value()}
        else:
            self.processing_thread.params = {}
        
        self.show_progress_dialog()
        self.processing_thread.start()
    
    def apply_adaptive_threshold(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        self.processing_thread.method = "adaptive_mean"
        self.processing_thread.image = self.original_image.copy()
        self.processing_thread.params = {
            'block_size': self.block_size_slider.value(),
            'C': self.c_slider.value()
        }
        
        self.show_progress_dialog()
        self.processing_thread.start()
    
    def apply_sharpen(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        self.processing_thread.method = "sharpen_laplacian"
        self.processing_thread.image = self.original_image.copy()
        self.processing_thread.params = {
            'strength': self.strength_slider.value() / 100.0
        }
        
        self.show_progress_dialog()
        self.processing_thread.start()
    
    def reset_image(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_images()


def main():
    app = QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
