import sys
import math
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QLabel, QSpinBox, 
                            QPushButton, QGroupBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPalette

class CanvasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.grid_size = 20
        self.points = []
        self.algorithm = "DDA"
        self.start_point = QPoint(0, 0)
        self.end_point = QPoint(10, 8)
        self.circle_center = QPoint(0, 0)
        self.circle_radius = 5
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)
        
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.update()
        
    def set_line_points(self, x1, y1, x2, y2):
        self.start_point = QPoint(x1, y1)
        self.end_point = QPoint(x2, y2)
        self.update()
        
    def set_circle_params(self, cx, cy, r):
        self.circle_center = QPoint(cx, cy)
        self.circle_radius = r
        self.update()
        
    def dda_line(self, x1, y1, x2, y2):
        points = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            points.append((round(x1), round(y1)))
            return points
            
        x_inc = dx / steps
        y_inc = dy / steps
        
        x = x1
        y = y1
        
        for i in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc
            
        return points
        
    def bresenham_line(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            points.append((x, y))
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
                
        return points
        
    def step_by_step_line(self, x1, y1, x2, y2):
        points = []
        if x1 == x2:
            y_start, y_end = min(y1, y2), max(y1, y2)
            for y in range(y_start, y_end + 1):
                points.append((x1, y))
        else:
            k = (y2 - y1) / (x2 - x1)
            b = y1 - k * x1
            
            if abs(k) <= 1:
                x_start, x_end = min(x1, x2), max(x1, x2)
                for x in range(x_start, x_end + 1):
                    y = round(k * x + b)
                    points.append((x, y))
            else:
                y_start, y_end = min(y1, y2), max(y1, y2)
                for y in range(y_start, y_end + 1):
                    x = round((y - b) / k)
                    points.append((x, y))
                    
        return points
        
    def bresenham_circle(self, cx, cy, r):
        points = []
        x = 0
        y = r
        d = 3 - 2 * r
        
        def add_circle_points(xc, yc, x, y):
            points.extend([
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x)
            ])
        
        add_circle_points(cx, cy, x, y)
        
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            add_circle_points(cx, cy, x, y)
            
        return points

    def wu_line(self, x1, y1, x2, y2):
        """Алгоритм Кастла-Питвея (Wu) для сглаживания линий"""
        points_with_intensity = []
        
        def ipart(x):
            return math.floor(x)
        
        def round(x):
            return ipart(x + 0.5)
        
        def fpart(x):
            return x - math.floor(x)
        
        def rfpart(x):
            return 1 - fpart(x)
        
        steep = abs(y2 - y1) > abs(x2 - x1)
        
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0:
            gradient = 1.0
        else:
            gradient = dy / dx
        
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)
        
        if steep:
            points_with_intensity.append((ypxl1, xpxl1, rfpart(yend) * xgap))
            points_with_intensity.append((ypxl1 + 1, xpxl1, fpart(yend) * xgap))
        else:
            points_with_intensity.append((xpxl1, ypxl1, rfpart(yend) * xgap))
            points_with_intensity.append((xpxl1, ypxl1 + 1, fpart(yend) * xgap))
        
        intery = yend + gradient
        
        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = fpart(x2 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)
        
        if steep:
            points_with_intensity.append((ypxl2, xpxl2, rfpart(yend) * xgap))
            points_with_intensity.append((ypxl2 + 1, xpxl2, fpart(yend) * xgap))
        else:
            points_with_intensity.append((xpxl2, ypxl2, rfpart(yend) * xgap))
            points_with_intensity.append((xpxl2, ypxl2 + 1, fpart(yend) * xgap))
        
        if steep:
            for x in range(int(xpxl1) + 1, int(xpxl2)):
                y1 = ipart(intery)
                points_with_intensity.append((y1, x, rfpart(intery)))
                points_with_intensity.append((y1 + 1, x, fpart(intery)))
                intery += gradient
        else:
            for x in range(int(xpxl1) + 1, int(xpxl2)):
                y1 = ipart(intery)
                points_with_intensity.append((x, y1, rfpart(intery)))
                points_with_intensity.append((x, y1 + 1, fpart(intery)))
                intery += gradient
        
        return points_with_intensity
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.draw_grid(painter)
        self.draw_axes(painter)
        self.draw_algorithm(painter)
        
    def draw_grid(self, painter):
        painter.setPen(QPen(QColor(240, 240, 240), 1))
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        for x in range(center_x % self.grid_size, width, self.grid_size):
            painter.drawLine(x, 0, x, height)
            
        for y in range(center_y % self.grid_size, height, self.grid_size):
            painter.drawLine(0, y, width, y)
            
    def draw_axes(self, painter):
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        painter.drawLine(0, center_y, width, center_y)
        painter.drawLine(center_x, 0, center_x, height)
        
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(width - 25, center_y - 15, "X")
        painter.drawText(center_x + 15, 25, "Y")
        
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        for i in range(center_x % self.grid_size, width, self.grid_size):
            if i != center_x:
                painter.drawLine(i, center_y - 4, i, center_y + 4)
                
        for i in range(center_y % self.grid_size, height, self.grid_size):
            if i != center_y:
                painter.drawLine(center_x - 4, i, center_x + 4, i)
                
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QPen(QColor(0, 0, 0)))
        scale = self.grid_size
        for i in range(center_x + scale, width, scale):
            value = (i - center_x) // scale
            painter.drawText(i - 8, center_y + 18, str(value))
            
        for i in range(center_x - scale, 0, -scale):
            value = (i - center_x) // scale
            painter.drawText(i - 8, center_y + 18, str(value))
            
        for i in range(center_y + scale, height, scale):
            value = -(i - center_y) // scale
            painter.drawText(center_x + 8, i + 8, str(value))
            
        for i in range(center_y - scale, 0, -scale):
            value = -(i - center_y) // scale
            painter.drawText(center_x + 8, i + 8, str(value))
            
        painter.drawText(center_x - 12, center_y + 18, "0")
        
    def draw_algorithm(self, painter):
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        scale = self.grid_size
        
        def to_screen(x, y):
            return center_x + x * scale, center_y - y * scale
            
        colors = {
            "DDA": QColor(255, 100, 100),
            "Bresenham Line": QColor(100, 150, 255),
            "Step-by-Step": QColor(100, 200, 100),
            "Bresenham Circle": QColor(200, 100, 200),
            "Wu Line": QColor(255, 150, 50)
        }
        
        if self.algorithm in ["DDA", "Bresenham Line", "Step-by-Step"]:
            painter.setPen(QPen(colors.get(self.algorithm, QColor(255, 100, 100)), 6))
            
            x1, y1 = to_screen(self.start_point.x(), self.start_point.y())
            x2, y2 = to_screen(self.end_point.x(), self.end_point.y())
            
            if self.algorithm == "DDA":
                points = self.dda_line(self.start_point.x(), self.start_point.y(),
                                     self.end_point.x(), self.end_point.y())
            elif self.algorithm == "Bresenham Line":
                points = self.bresenham_line(self.start_point.x(), self.start_point.y(),
                                           self.end_point.x(), self.end_point.y())
            else:
                points = self.step_by_step_line(self.start_point.x(), self.start_point.y(),
                                              self.end_point.x(), self.end_point.y())
                
            for x, y in points:
                sx, sy = to_screen(x, y)
                painter.drawEllipse(int(sx) - 3, int(sy) - 3, 6, 6)
                
        elif self.algorithm == "Bresenham Circle":
            painter.setPen(QPen(colors.get(self.algorithm), 6))
            
            points = self.bresenham_circle(self.circle_center.x(), self.circle_center.y(),
                                         self.circle_radius)
            
            for x, y in points:
                sx, sy = to_screen(x, y)
                painter.drawEllipse(int(sx) - 3, int(sy) - 3, 6, 6)
                
        elif self.algorithm == "Wu Line":
            points_with_intensity = self.wu_line(self.start_point.x(), self.start_point.y(),
                                               self.end_point.x(), self.end_point.y())
            
            for x, y, intensity in points_with_intensity:
                sx, sy = to_screen(x, y)
                alpha = int(intensity * 255)
                color = QColor(255, 150, 50, alpha)
                painter.setPen(QPen(color, 6))
                painter.drawEllipse(int(sx) - 2, int(sy) - 2, 4, 4)

class StyledGroupBox(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #000000;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Базовые растровые алгоритмы - Лабораторная работа 4")
        self.setGeometry(100, 100, 1400, 900)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                color: #000000;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                margin: 4px 2px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QComboBox {
                padding: 4px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                color: #000000;
            }
            QComboBox:focus {
                border: 1px solid #4CAF50;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #cccccc;
                color: #000000;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
            QSpinBox {
                padding: 4px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                color: #000000;
            }
            QTextEdit {
                padding: 4px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                color: #000000;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
            QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
                border: 1px solid #4CAF50;
            }
            QLabel {
                color: #000000;
                font-weight: bold;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e0e0e0; }")
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("Управление алгоритмами")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)
        
        algo_group = StyledGroupBox("Выбор алгоритма")
        algo_layout = QVBoxLayout(algo_group)
        
        algo_layout.addWidget(QLabel("Алгоритм:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["DDA", "Bresenham Line", "Step-by-Step", "Bresenham Circle", "Wu Line"])
        self.algo_combo.currentTextChanged.connect(self.on_algorithm_changed)
        algo_layout.addWidget(self.algo_combo)
        
        left_layout.addWidget(algo_group)
        
        self.line_group = StyledGroupBox("Параметры линии")
        line_layout = QVBoxLayout(self.line_group)
        
        point1_layout = QHBoxLayout()
        point1_layout.addWidget(QLabel("Точка A:"))
        point1_layout.addStretch()
        point1_layout.addWidget(QLabel("X₁:"))
        self.x1_spin = QSpinBox()
        self.x1_spin.setRange(-50, 50)
        self.x1_spin.setValue(0)
        self.x1_spin.setSuffix(" ед.")
        point1_layout.addWidget(self.x1_spin)
        
        point1_layout.addWidget(QLabel("Y₁:"))
        self.y1_spin = QSpinBox()
        self.y1_spin.setRange(-50, 50)
        self.y1_spin.setValue(0)
        self.y1_spin.setSuffix(" ед.")
        point1_layout.addWidget(self.y1_spin)
        line_layout.addLayout(point1_layout)
        
        point2_layout = QHBoxLayout()
        point2_layout.addWidget(QLabel("Точка B:"))
        point2_layout.addStretch()
        point2_layout.addWidget(QLabel("X₂:"))
        self.x2_spin = QSpinBox()
        self.x2_spin.setRange(-50, 50)
        self.x2_spin.setValue(10)
        self.x2_spin.setSuffix(" ед.")
        point2_layout.addWidget(self.x2_spin)
        
        point2_layout.addWidget(QLabel("Y₂:"))
        self.y2_spin = QSpinBox()
        self.y2_spin.setRange(-50, 50)
        self.y2_spin.setValue(8)
        self.y2_spin.setSuffix(" ед.")
        point2_layout.addWidget(self.y2_spin)
        line_layout.addLayout(point2_layout)
        
        left_layout.addWidget(self.line_group)
        
        self.circle_group = StyledGroupBox("Параметры окружности")
        circle_layout = QVBoxLayout(self.circle_group)
        
        center_layout = QHBoxLayout()
        center_layout.addWidget(QLabel("Центр:"))
        center_layout.addStretch()
        center_layout.addWidget(QLabel("X:"))
        self.cx_spin = QSpinBox()
        self.cx_spin.setRange(-50, 50)
        self.cx_spin.setValue(0)
        self.cx_spin.setSuffix(" ед.")
        center_layout.addWidget(self.cx_spin)
        
        center_layout.addWidget(QLabel("Y:"))
        self.cy_spin = QSpinBox()
        self.cy_spin.setRange(-50, 50)
        self.cy_spin.setValue(0)
        self.cy_spin.setSuffix(" ед.")
        center_layout.addWidget(self.cy_spin)
        circle_layout.addLayout(center_layout)
        
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Радиус:"))
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 50)
        self.radius_spin.setValue(5)
        self.radius_spin.setSuffix(" ед.")
        radius_layout.addWidget(self.radius_spin)
        radius_layout.addStretch()
        circle_layout.addLayout(radius_layout)
        
        left_layout.addWidget(self.circle_group)
        
        self.apply_btn = QPushButton("Применить параметры")
        self.apply_btn.clicked.connect(self.on_apply_parameters)
        left_layout.addWidget(self.apply_btn)
        
        calc_group = StyledGroupBox("Вычисления и время выполнения")
        calc_layout = QVBoxLayout(calc_group)
        
        self.calc_text = QTextEdit()
        self.calc_text.setMaximumHeight(250)
        self.calc_text.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        calc_layout.addWidget(self.calc_text)
        
        left_layout.addWidget(calc_group)
        left_layout.addStretch()
        
        self.canvas = CanvasWidget()
        self.canvas.setStyleSheet("""
            CanvasWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(self.canvas)
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        
        self.on_algorithm_changed("DDA")
        self.update_calculations()
        
    def on_algorithm_changed(self, algorithm):
        self.canvas.set_algorithm(algorithm)
        if algorithm == "Bresenham Circle":
            self.line_group.hide()
            self.circle_group.show()
        else:
            self.line_group.show()
            self.circle_group.hide()
        self.update_calculations()
        
    def on_apply_parameters(self):
        algorithm = self.algo_combo.currentText()
        
        if algorithm == "Bresenham Circle":
            self.canvas.set_circle_params(
                self.cx_spin.value(),
                self.cy_spin.value(),
                self.radius_spin.value()
            )
        else:
            self.canvas.set_line_points(
                self.x1_spin.value(),
                self.y1_spin.value(),
                self.x2_spin.value(),
                self.y2_spin.value()
            )
            
        self.update_calculations()
        
    def update_calculations(self):
        algorithm = self.algo_combo.currentText()
        text = ""
        
        if algorithm in ["DDA", "Bresenham Line", "Step-by-Step", "Wu Line"]:
            x1, y1 = self.x1_spin.value(), self.y1_spin.value()
            x2, y2 = self.x2_spin.value(), self.y2_spin.value()
            
            text += f"Отрезок от A({x1}, {y1}) до B({x2}, {y2})\n"
            text += "─" * 50 + "\n\n"
            
            start_time = time.time()
            
            if algorithm == "DDA":
                points = self.canvas.dda_line(x1, y1, x2, y2)
                text += "Алгоритм ЦДА (Digital Differential Analyzer):\n"
                text += f"   Δx = {x2 - x1}, Δy = {y2 - y1}\n"
                steps = max(abs(x2 - x1), abs(y2 - y1))
                text += f"   steps = max(|Δx|, |Δy|) = {steps}\n"
                if steps > 0:
                    text += f"   x_inc = Δx/steps = {(x2 - x1)/steps:.3f}\n"
                    text += f"   y_inc = Δy/steps = {(y2 - y1)/steps:.3f}\n"
                
            elif algorithm == "Bresenham Line":
                points = self.canvas.bresenham_line(x1, y1, x2, y2)
                text += "Алгоритм Брезенхема (отрезок):\n"
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                text += f"   dx = {dx}, dy = {dy}\n"
                text += f"   начальная ошибка err = dx - dy = {dx - dy}\n"
                
            elif algorithm == "Step-by-Step":
                points = self.canvas.step_by_step_line(x1, y1, x2, y2)
                text += "Пошаговый алгоритм:\n"
                if x1 == x2:
                    text += "   Вертикальная линия (x = const)\n"
                else:
                    k = (y2 - y1) / (x2 - x1)
                    b = y1 - k * x1
                    text += f"   Уравнение: y = {k:.3f}x + {b:.3f}\n"
                    if abs(k) <= 1:
                        text += "   Итерация по оси X\n"
                    else:
                        text += "   Итерация по оси Y\n"
                        
            elif algorithm == "Wu Line":
                points_with_intensity = self.canvas.wu_line(x1, y1, x2, y2)
                text += "Алгоритм Кастла-Питвея (Wu) - сглаживание:\n"
                text += "   Использует антиалиасинг для сглаживания ступенек\n"
                text += "   Каждый пиксель рисуется с интенсивностью от 0 до 1\n"
                text += "   Интенсивность зависит от расстояния до идеальной линии\n"
                text += "   Создает плавные переходы между пикселями\n"
                points = [(x, y) for x, y, intensity in points_with_intensity]
                        
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            text += f"\nРезультаты:\n"
            if algorithm == "Wu Line":
                text += f"   Количество точек: {len(points_with_intensity)}\n"
                text += f"   Первые 10 точек с интенсивностью: {points_with_intensity[:10]}\n"
            else:
                text += f"   Количество точек: {len(points)}\n"
                text += f"   Первые 10 точек: {points[:10]}\n"
            text += f"   Время выполнения: {execution_time:.6f} мс\n"
            
        else:
            cx, cy, r = self.cx_spin.value(), self.cy_spin.value(), self.radius_spin.value()
            
            text += f"Окружность с центром O({cx}, {cy}) и радиусом R = {r}\n"
            text += "─" * 50 + "\n\n"
            
            start_time = time.time()
            points = self.canvas.bresenham_circle(cx, cy, r)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            text += "Алгоритм Брезенхема (окружность):\n"
            text += f"   Начальные значения: x = 0, y = {r}\n"
            text += f"   Начальная ошибка d = 3 - 2R = {3 - 2*r}\n"
            text += f"   Рисуется 1/8 окружности с симметрией\n"
            
            text += f"\nРезультаты:\n"
            text += f"   Количество точек: {len(points)}\n"
            text += f"   Первые 10 точек: {points[:10]}\n"
            text += f"   Время выполнения: {execution_time:.6f} мс\n"
            
        self.calc_text.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
