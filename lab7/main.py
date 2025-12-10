import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPaintEvent


class Matrix4x4:
    """Реализация матрицы 4x4 для 3D преобразований"""
    
    def __init__(self, data=None):
        if data is None:
            self.data = [[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]]
        else:
            self.data = data
    
    def identity(self):
        return Matrix4x4([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])
    
    def multiply(self, other):
        result = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix4x4(result)
    
    def translate(self, tx, ty, tz):
        trans = [[1, 0, 0, tx],
                 [0, 1, 0, ty],
                 [0, 0, 1, tz],
                 [0, 0, 0, 1]]
        return self.multiply(Matrix4x4(trans))
    
    def scale(self, sx, sy, sz):
        scale = [[sx, 0, 0, 0],
                 [0, sy, 0, 0],
                 [0, 0, sz, 0],
                 [0, 0, 0, 1]]
        return self.multiply(Matrix4x4(scale))
    
    def rotate_x(self, angle_deg):
        angle = math.radians(angle_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rot = [[1, 0, 0, 0],
               [0, cos_a, -sin_a, 0],
               [0, sin_a, cos_a, 0],
               [0, 0, 0, 1]]
        return self.multiply(Matrix4x4(rot))
    
    def rotate_y(self, angle_deg):
        angle = math.radians(angle_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rot = [[cos_a, 0, sin_a, 0],
               [0, 1, 0, 0],
               [-sin_a, 0, cos_a, 0],
               [0, 0, 0, 1]]
        return self.multiply(Matrix4x4(rot))
    
    def rotate_z(self, angle_deg):
        angle = math.radians(angle_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rot = [[cos_a, -sin_a, 0, 0],
               [sin_a, cos_a, 0, 0],
               [0, 0, 1, 0],
               [0, 0, 0, 1]]
        return self.multiply(Matrix4x4(rot))
    
    def transform_point(self, point):
        x, y, z = point
        result = [0, 0, 0, 0]
        vector = [x, y, z, 1]
        
        for i in range(4):
            for j in range(4):
                result[i] += self.data[i][j] * vector[j]
        
        w = result[3]
        if w != 0:
            return (result[0]/w, result[1]/w, result[2]/w)
        return (result[0], result[1], result[2])
    
    def __str__(self):
        lines = []
        for row in self.data:
            line = "[ " + " ".join(f"{val:8.3f}" for val in row) + " ]"
            lines.append(line)
        return "\n".join(lines)


class Letter3DModel:
    """3D модель буквы 'K' с геометрией и преобразованиями"""
    
    def __init__(self):
        self.vertices = self.create_letter_vertices()
        self.edges = self.create_letter_edges()
        self.matrix = Matrix4x4()
        
    def create_letter_vertices(self):
        vertices = []
        thickness = 15
        
        height = 160
        width = 80
        leg_width = 60
        leg_length = 120
        
        vertices.extend([
            (-width/2, -height/2, -thickness/2),
            (-width/2, height/2, -thickness/2),
            (width/2, -height/2, -thickness/2),
            (width/2, height/2, -thickness/2),
        ])
        
        vertices.extend([
            (-width/2, -height/2, thickness/2),
            (-width/2, height/2, thickness/2),
            (width/2, -height/2, thickness/2),
            (width/2, height/2, thickness/2),
        ])
        
        start_y = height/4
        
        vertices.extend([
            (width/2, start_y, -thickness/2),
            (width/2 + leg_length, height/2, -thickness/2),
            (width/2 + leg_length + leg_width, height/2 - leg_width/2, -thickness/2),
            (width/2, start_y - leg_width, -thickness/2),
        ])
        
        vertices.extend([
            (width/2, start_y, thickness/2),
            (width/2 + leg_length, height/2, thickness/2),
            (width/2 + leg_length + leg_width, height/2 - leg_width/2, thickness/2),
            (width/2, start_y - leg_width, thickness/2),
        ])
        
        vertices.extend([
            (width/2, -start_y, -thickness/2),
            (width/2 + leg_length, -height/2, -thickness/2),
            (width/2 + leg_length + leg_width, -height/2 + leg_width/2, -thickness/2),
            (width/2, -start_y + leg_width, -thickness/2),
        ])
        
        vertices.extend([
            (width/2, -start_y, thickness/2),
            (width/2 + leg_length, -height/2, thickness/2),
            (width/2 + leg_length + leg_width, -height/2 + leg_width/2, thickness/2),
            (width/2, -start_y + leg_width, thickness/2),
        ])
        
        return vertices
    
    def create_letter_edges(self):
        edges = []
        
        edges.extend([(0, 1), (0, 2), (1, 3), (2, 3)])
        edges.extend([(4, 5), (4, 6), (5, 7), (6, 7)])
        edges.extend([(0, 4), (1, 5), (2, 6), (3, 7)])
        edges.extend([(8, 9), (9, 10), (10, 11), (11, 8)])
        edges.extend([(12, 13), (13, 14), (14, 15), (15, 12)])
        edges.extend([(8, 12), (9, 13), (10, 14), (11, 15)])
        edges.extend([(16, 17), (17, 18), (18, 19), (19, 16)])
        edges.extend([(20, 21), (21, 22), (22, 23), (23, 20)])
        edges.extend([(16, 20), (17, 21), (18, 22), (19, 23)])
        edges.extend([(3, 8), (2, 11)])
        edges.extend([(7, 12), (6, 15)])
        edges.extend([(2, 16), (3, 19)])
        edges.extend([(6, 20), (7, 23)])
        edges.extend([(8, 11), (9, 10)])
        edges.extend([(16, 19), (17, 18)])
        
        return edges
    
    def apply_transformation(self, tx=0, ty=0, tz=0, 
                           scale=1.0, rx=0, ry=0, rz=0):
        self.matrix = Matrix4x4().identity()
        self.matrix = self.matrix.scale(scale, scale, scale)
        self.matrix = self.matrix.rotate_x(rx)
        self.matrix = self.matrix.rotate_y(ry)
        self.matrix = self.matrix.rotate_z(rz)
        self.matrix = self.matrix.translate(tx, ty, tz)
    
    def get_transformed_vertices(self):
        return [self.matrix.transform_point(v) for v in self.vertices]
    
    def project_to_2d(self, projection_mode="3D", width=800, height=600):
        cx, cy = width // 2, height // 2
        transformed = self.get_transformed_vertices()
        projected_points = []
        
        for x, y, z in transformed:
            if projection_mode == "XY":
                px = cx + x
                py = cy - y
            elif projection_mode == "XZ":
                px = cx + x
                py = cy - z
            elif projection_mode == "YZ":
                px = cx + y
                py = cy - z
            else:
                perspective = 600
                scale = perspective / (perspective + z + 200)
                px = cx + x * scale
                py = cy - y * scale
            
            projected_points.append((px, py))
        
        return projected_points


class CanvasWidget(QWidget):
    """Виджет для отображения 3D модели"""
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.projection_mode = "3D"
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        
    def set_projection(self, mode):
        self.projection_mode = mode
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(self.rect(), Qt.white)
        
        self.draw_axes(painter)
        
        points = self.model.project_to_2d(self.projection_mode, 
                                         self.width(), self.height())
        
        painter.setPen(QPen(QColor(52, 152, 219), 2))
        for v1, v2 in self.model.edges:
            if 0 <= v1 < len(points) and 0 <= v2 < len(points):
                x1, y1 = points[v1]
                x2, y2 = points[v2]
                painter.drawLine(x1, y1, x2, y2)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(231, 76, 60))
        for x, y in points:
            painter.drawEllipse(int(x-2), int(y-2), 4, 4)
        
        painter.setFont(QFont("Arial", 10))
        proj_names = {
            "3D": "3D проекция с перспективой",
            "XY": "OXY проекция",
            "XZ": "OXZ проекция",
            "YZ": "OYZ проекция"
        }
        painter.drawText(10, 20, f"Режим: {proj_names.get(self.projection_mode, self.projection_mode)}")
    
    def draw_axes(self, painter):
        width, height = self.width(), self.height()
        cx, cy = width // 2, height // 2
        
        painter.setPen(QPen(QColor(204, 204, 204), 1))
        
        painter.drawLine(0, cy, width, cy)
        painter.drawLine(cx, 0, cx, height)
        
        painter.setPen(QColor(102, 102, 102))
        painter.setFont(QFont("Arial", 12))
        
        labels = {
            "XY": ("X", "Y"),
            "XZ": ("X", "Z"),
            "YZ": ("Y", "Z"),
            "3D": ("X", "Y", "Z")
        }
        
        label_x, label_y = labels[self.projection_mode][:2]
        
        painter.drawText(width - 30, cy + 20, label_x)
        painter.drawText(cx - 20, 20, label_y)
        
        if self.projection_mode == "3D":
            painter.drawLine(cx, cy, cx + 60, cy - 60)
            painter.drawText(cx + 70, cy - 70, "Z")


class ControlGroup(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


class SliderControl(QWidget):
    value_changed = None
    
    def __init__(self, label, min_val, max_val, default_val=0, step=1):
        super().__init__()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QLabel(label)
        self.value_label = QLabel(str(default_val))
        self.value_label.setAlignment(Qt.AlignCenter)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(min_val * 10, max_val * 10)
        self.slider.setValue(default_val * 10)
        self.slider.setSingleStep(step * 10)
        
        labels_layout = QHBoxLayout()
        labels_layout.addWidget(self.label)
        labels_layout.addWidget(self.value_label)
        
        self.layout.addLayout(labels_layout)
        self.layout.addWidget(self.slider)
        
        self.slider.valueChanged.connect(self.update_value_label)
    
    def update_value_label(self, value):
        self.value_label.setText(f"{value/10:.1f}")
        if self.value_changed:
            self.value_changed(value/10)
    
    def get_value(self):
        return self.slider.value() / 10
    
    def set_value(self, value):
        self.slider.setValue(int(value * 10))


class TransformationControls(QWidget):
    transformation_changed = None
    reset_requested = None
    
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        self.translate_x = SliderControl("Перенос X:", -200, 200, 0)
        self.translate_y = SliderControl("Перенос Y:", -200, 200, 0)
        self.translate_z = SliderControl("Перенос Z:", -200, 200, 0)
        
        self.scale = SliderControl("Масштаб:", 0.1, 3, 1, 0.1)
        
        self.rotate_x = SliderControl("Вращение X:", 0, 360, 0)
        self.rotate_y = SliderControl("Вращение Y:", 0, 360, 0)
        self.rotate_z = SliderControl("Вращение Z:", 0, 360, 0)
        
        layout.addWidget(self.translate_x, 0, 0)
        layout.addWidget(self.translate_y, 0, 1)
        layout.addWidget(self.translate_z, 0, 2)
        
        layout.addWidget(self.scale, 1, 0, 1, 3)
        
        layout.addWidget(self.rotate_x, 2, 0)
        layout.addWidget(self.rotate_y, 2, 1)
        layout.addWidget(self.rotate_z, 2, 2)
        
        self.reset_button = QPushButton("Сбросить преобразования")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.reset_button, 3, 0, 1, 3)
        
        self.reset_button.clicked.connect(self.reset_all)
        
        for slider in [self.translate_x, self.translate_y, self.translate_z,
                      self.scale, self.rotate_x, self.rotate_y, self.rotate_z]:
            slider.value_changed = self.on_transformation_changed
    
    def on_transformation_changed(self, value):
        if self.transformation_changed:
            self.get_values()
    
    def get_values(self):
        if self.transformation_changed:
            self.transformation_changed({
                'tx': self.translate_x.get_value(),
                'ty': self.translate_y.get_value(),
                'tz': self.translate_z.get_value(),
                'scale': self.scale.get_value(),
                'rx': self.rotate_x.get_value(),
                'ry': self.rotate_y.get_value(),
                'rz': self.rotate_z.get_value()
            })
    
    def reset_all(self):
        self.translate_x.set_value(0)
        self.translate_y.set_value(0)
        self.translate_z.set_value(0)
        self.scale.set_value(1)
        self.rotate_x.set_value(0)
        self.rotate_y.set_value(0)
        self.rotate_z.set_value(0)
        
        if self.reset_requested:
            self.reset_requested()


class ProjectionButtons(QWidget):
    projection_changed = None
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.buttons = {}
        projections = [
            ("OXY проекция", "XY"),
            ("OXZ проекция", "XZ"),
            ("OYZ проекция", "YZ"),
            ("3D вид", "3D")
        ]
        
        for text, mode in projections:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=mode: self.on_button_clicked(m))
            layout.addWidget(btn)
            self.buttons[mode] = btn
        
        self.buttons["3D"].setChecked(True)
        self.buttons["3D"].setStyleSheet("background-color: #2c3e50; color: white;")
    
    def on_button_clicked(self, mode):
        for btn in self.buttons.values():
            btn.setStyleSheet("")
        
        self.buttons[mode].setStyleSheet("background-color: #2c3e50; color: white;")
        
        if self.projection_changed:
            self.projection_changed(mode)


class MatrixDisplay(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Матрица преобразования:")
        title.setStyleSheet("font-weight: bold; color: #3498db; font-size: 14px;")
        layout.addWidget(title)
        
        self.matrix_text = QLabel("")
        self.matrix_text.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #f8f9fa;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.matrix_text.setWordWrap(True)
        
        layout.addWidget(self.matrix_text)
    
    def update_matrix(self, matrix_str):
        self.matrix_text.setText(matrix_str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.model = Letter3DModel()
        
        self.setWindowTitle("3D Визуализация буквы 'К'")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        title = QLabel("3D Визуализация буквы 'К'")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        trans_group = ControlGroup("Преобразования")
        self.trans_controls = TransformationControls()
        trans_group.layout.addWidget(self.trans_controls)
        left_layout.addWidget(trans_group)
        
        proj_group = ControlGroup("Проекции")
        self.proj_buttons = ProjectionButtons()
        proj_group.layout.addWidget(self.proj_buttons)
        left_layout.addWidget(proj_group)
        
        matrix_group = ControlGroup("Матрица преобразования")
        self.matrix_display = MatrixDisplay()
        matrix_group.layout.addWidget(self.matrix_display)
        left_layout.addWidget(matrix_group)
        
        content_layout.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        self.canvas = CanvasWidget(self.model)
        right_layout.addWidget(self.canvas)
        
        content_layout.addWidget(right_panel)
        
        self.connect_signals()
        
        self.update_transformation()
    
    def connect_signals(self):
        self.trans_controls.transformation_changed = self.update_transformation
        self.trans_controls.reset_requested = self.reset_transformation
        self.proj_buttons.projection_changed = self.update_projection
    
    def update_transformation(self, values=None):
        if values:
            self.model.apply_transformation(**values)
        else:
            values = {
                'tx': self.trans_controls.translate_x.get_value(),
                'ty': self.trans_controls.translate_y.get_value(),
                'tz': self.trans_controls.translate_z.get_value(),
                'scale': self.trans_controls.scale.get_value(),
                'rx': self.trans_controls.rotate_x.get_value(),
                'ry': self.trans_controls.rotate_y.get_value(),
                'rz': self.trans_controls.rotate_z.get_value()
            }
            self.model.apply_transformation(**values)
        
        self.canvas.update()
        self.update_matrix_display()
    
    def reset_transformation(self):
        self.update_transformation({
            'tx': 0, 'ty': 0, 'tz': 0,
            'scale': 1.0,
            'rx': 0, 'ry': 0, 'rz': 0
        })
    
    def update_projection(self, mode):
        self.canvas.set_projection(mode)
    
    def update_matrix_display(self):
        self.matrix_display.update_matrix(str(self.model.matrix))


def main():
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:checked {
            background-color: #2c3e50;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background: #ddd;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #3498db;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
