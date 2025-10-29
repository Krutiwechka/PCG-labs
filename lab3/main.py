import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QSlider, 
                               QComboBox, QGroupBox, QFileDialog, QMessageBox,
                               QSplitter, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QAction

class ImageProcessor:
    @staticmethod
    def global_threshold_otsu(image): #Оцу
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresholded
    
    @staticmethod
    def global_threshold_iterative(image, max_iterations=100, tolerance=1): #Итеративный
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        threshold = np.mean(gray)
        
        for i in range(max_iterations):
            foreground = gray[gray > threshold]
            background = gray[gray <= threshold]
            
            if len(foreground) == 0 or len(background) == 0:
                break
                
            new_threshold = (np.mean(foreground) + np.mean(background)) / 2
            
            if abs(new_threshold - threshold) < tolerance:
                break
                
            threshold = new_threshold
        
        _, thresholded = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        return thresholded, threshold
    
    @staticmethod
    def global_threshold_manual(image, threshold_value): #ручная
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        _, thresholded = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        return thresholded
    
    @staticmethod
    def adaptive_threshold_mean(image, block_size=11, C=2): #адаптивная пороговая
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        if block_size % 2 == 0:
            block_size += 1
        
        thresholded = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, block_size, C
        )
        return thresholded
    
    @staticmethod
    def sharpen_filter_laplacian(image, strength=1.0):
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
            dst = np.zeros_like(image, dtype=np.float32)
            for c in range(ch):
                channel = image[:, :, c].astype(np.float32)
                filtered = cv2.filter2D(channel, cv2.CV_32F, kernel)
                dst[:, :, c] = filtered
            dst = np.clip(dst, 0, 255).astype(np.uint8)
            return dst
        else:
            gray = image.astype(np.float32)
            filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
            filtered = np.clip(filtered, 0, 255).astype(np.uint8)
            return filtered

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
        
        # Убрали выбор метода, оставили только Лапласиан
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
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.processed_image = self.original_image.copy()
                self.display_images()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
    
    def save_image(self):
        if self.processed_image is None:
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "", 
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        
        if file_path:
            success = cv2.imwrite(file_path, self.processed_image)
            if success:
                QMessageBox.information(self, "Успех", "Изображение сохранено")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изображение")
    
    def display_images(self):
        if self.original_image is not None:
            original_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            original_qimage = QImage(
                original_rgb.data, 
                original_rgb.shape[1], 
                original_rgb.shape[0], 
                original_rgb.strides[0], 
                QImage.Format_RGB888
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
                processed_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
                processed_qimage = QImage(
                    processed_rgb.data,
                    processed_rgb.shape[1],
                    processed_rgb.shape[0],
                    processed_rgb.strides[0],
                    QImage.Format_RGB888
                )
            self.processed_viewer.setPixmap(QPixmap.fromImage(processed_qimage))
    
    def apply_global_threshold(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        method = self.global_method_combo.currentText()
        
        if method == "Метод Оцу":
            self.processed_image = ImageProcessor.global_threshold_otsu(self.original_image)
        elif method == "Итеративный метод":
            self.processed_image, threshold = ImageProcessor.global_threshold_iterative(self.original_image)
            QMessageBox.information(self, "Информация", f"Найденное пороговое значение: {threshold:.2f}")
        elif method == "Ручной метод":
            threshold_value = self.threshold_slider.value()
            self.processed_image = ImageProcessor.global_threshold_manual(self.original_image, threshold_value)
        
        self.display_images()
    
    def apply_adaptive_threshold(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        block_size = self.block_size_slider.value()
        C = self.c_slider.value()
        
        self.processed_image = ImageProcessor.adaptive_threshold_mean(
            self.original_image, block_size, C
        )
        
        self.display_images()
    
    def apply_sharpen(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        strength = self.strength_slider.value() / 100.0
        
        # Теперь используется только лапласиан
        self.processed_image = ImageProcessor.sharpen_filter_laplacian(
            self.original_image, strength
        )
        
        self.display_images()
    
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
