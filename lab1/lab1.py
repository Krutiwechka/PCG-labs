import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QLabel, QSlider, QSpinBox,
                             QDoubleSpinBox, QLineEdit, QPushButton, QColorDialog,
                             QMessageBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QFont

class ColorConverter:
    @staticmethod
    def rgb_to_xyz(r, g, b):
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        
        r = r if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g = g if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b = b if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
        
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        return x * 100, y * 100, z * 100
    
    @staticmethod
    def xyz_to_rgb(x, y, z):
        x = x / 100.0
        y = y / 100.0
        z = z / 100.0
        
        r = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
        g = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
        b = x * 0.0556434 + y * -0.2040259 + z * 1.0572252
        
        r = 12.92 * r if r <= 0.0031308 else (1.055 * (r ** (1/2.4))) - 0.055
        g = 12.92 * g if g <= 0.0031308 else (1.055 * (g ** (1/2.4))) - 0.055
        b = 12.92 * b if b <= 0.0031308 else (1.055 * (b ** (1/2.4))) - 0.055
        
        r = max(0, min(255, int(round(r * 255))))
        g = max(0, min(255, int(round(g * 255))))
        b = max(0, min(255, int(round(b * 255))))
        
        return r, g, b
    
    @staticmethod
    def rgb_to_hls(r, g, b):
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        
        l = (max_val + min_val) / 2.0
        
        if max_val == min_val:
            h = s = 0.0
        else:
            d = max_val - min_val
            s = d / (2.0 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            
            if max_val == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif max_val == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0
            
            h = h / 6.0
        
        return h * 360, l * 100, s * 100
    
    @staticmethod
    def hls_to_rgb(h, l, s):
        h = h / 360.0
        l = l / 100.0
        s = s / 100.0
        
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        r = max(0, min(255, int(round(r * 255))))
        g = max(0, min(255, int(round(g * 255))))
        b = max(0, min(255, int(round(b * 255))))
        
        return r, g, b
    
    @staticmethod
    def xyz_to_hls(x, y, z):
        rgb = ColorConverter.xyz_to_rgb(x, y, z)
        return ColorConverter.rgb_to_hls(*rgb)
    
    @staticmethod
    def hls_to_xyz(h, l, s):
        rgb = ColorConverter.hls_to_rgb(h, l, s)
        return ColorConverter.rgb_to_xyz(*rgb)

class ColorInputWidget(QWidget):
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label, min_val, max_val, decimals=0, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(label)
        
        if decimals == 0:
            self.spinbox = QSpinBox()
        else:
            self.spinbox = QDoubleSpinBox()
            self.spinbox.setDecimals(decimals)
            
        self.spinbox.setRange(min_val, max_val)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(int(min_val), int(max_val))
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.slider)
        
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
        self.slider.valueChanged.connect(self._on_slider_changed)
        
        self._updating = False
        self.decimals = decimals
    
    def set_value(self, value):
        self._updating = True
        self.spinbox.setValue(value)
        self.slider.setValue(int(value))
        self._updating = False
    
    def get_value(self):
        return self.spinbox.value()
    
    def _on_spinbox_changed(self, value):
        if not self._updating:
            self._updating = True
            self.slider.setValue(int(value))
            self._updating = False
            self.valueChanged.emit(float(value))
    
    def _on_slider_changed(self, value):
        if not self._updating:
            self._updating = True
            if self.decimals == 0:
                self.spinbox.setValue(int(value))
            else:
                self.spinbox.setValue(float(value))
            self._updating = False
            self.valueChanged.emit(float(value))

class ColorModelGroup(QGroupBox):
    valuesChanged = pyqtSignal()
    
    def __init__(self, title, labels, ranges, decimals, parent=None):
        super().__init__(title, parent)
        self.layout = QVBoxLayout(self)
        self.inputs = []
        
        for label, (min_val, max_val), decimal in zip(labels, ranges, decimals):
            input_widget = ColorInputWidget(label, min_val, max_val, decimal)
            input_widget.valueChanged.connect(self._on_input_changed)
            self.layout.addWidget(input_widget)
            self.inputs.append(input_widget)
    
    def set_values(self, values):
        for input_widget, value in zip(self.inputs, values):
            input_widget.set_value(value)
    
    def get_values(self):
        return [input_widget.get_value() for input_widget in self.inputs]
    
    def _on_input_changed(self, value):
        self.valuesChanged.emit()

class ColorDisplayWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setMinimumHeight(100)
        self.setAutoFillBackground(True)
        
        self.current_color = QColor(0, 0, 0)
        self.update_display()
    
    def set_color(self, r, g, b):
        self.current_color = QColor(int(r), int(g), int(b))
        self.update_display()
    
    def update_display(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, self.current_color)
        self.setPalette(palette)

class ColorConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.set_current_rgb(128, 128, 128)
        self.updating = False
    
    def init_ui(self):
        self.setWindowTitle("Конвертер цветовых моделей")
        self.setGeometry(100, 100, 900, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.color_display = ColorDisplayWidget()
        main_layout.addWidget(self.color_display)
        
        models_layout = QHBoxLayout()
        
        self.rgb_group = ColorModelGroup(
            "RGB",
            ["R:", "G:", "B:"],
            [(0, 255), (0, 255), (0, 255)],
            [0, 0, 0]
        )
        self.rgb_group.valuesChanged.connect(self.on_rgb_changed)
        models_layout.addWidget(self.rgb_group)
        
        self.xyz_group = ColorModelGroup(
            "XYZ",
            ["X:", "Y:", "Z:"],
            [(0, 100), (0, 100), (0, 100)],
            [2, 2, 2]
        )
        self.xyz_group.valuesChanged.connect(self.on_xyz_changed)
        models_layout.addWidget(self.xyz_group)
        
        self.hls_group = ColorModelGroup(
            "HLS",
            ["H:", "L:", "S:"],
            [(0, 360), (0, 100), (0, 100)],
            [1, 1, 1]
        )
        self.hls_group.valuesChanged.connect(self.on_hls_changed)
        models_layout.addWidget(self.hls_group)
        
        main_layout.addLayout(models_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.palette_btn = QPushButton("Выбрать из палитры")
        self.palette_btn.clicked.connect(self.show_color_dialog)
        buttons_layout.addWidget(self.palette_btn)
        
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("Введите HEX цвет (#RRGGBB)")
        self.hex_input.editingFinished.connect(self.on_hex_changed)
        buttons_layout.addWidget(QLabel("HEX:"))
        buttons_layout.addWidget(self.hex_input)
        
        main_layout.addLayout(buttons_layout)
        
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setVisible(False)
        self.warning_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.warning_label)
    
    def set_current_rgb(self, r, g, b):
        self.current_rgb = (r, g, b)
        self.color_display.set_color(r, g, b)
        self.hex_input.setText(f"#{r:02x}{g:02x}{b:02x}".upper())
        
        self.updating = True
        self.rgb_group.set_values([r, g, b])
        
        x, y, z = ColorConverter.rgb_to_xyz(r, g, b)
        self.xyz_group.set_values([x, y, z])
        
        h, l, s = ColorConverter.rgb_to_hls(r, g, b)
        self.hls_group.set_values([h, l, s])
        self.updating = False
    
    def on_rgb_changed(self):
        if self.updating:
            return
            
        self.updating = True
        r, g, b = self.rgb_group.get_values()
        r, g, b = int(r), int(g), int(b)
        
        if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
            self.show_warning("RGB значения обрезаны до допустимого диапазона")
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            self.rgb_group.set_values([r, g, b])
        
        self.set_current_rgb(r, g, b)
        self.updating = False
    
    def on_xyz_changed(self):
        if self.updating:
            return
            
        self.updating = True
        x, y, z = self.xyz_group.get_values()
        
        try:
            r, g, b = ColorConverter.xyz_to_rgb(x, y, z)
            
            if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
                self.show_warning("XYZ значения приводят к выходу за границы RGB")
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
            
            self.current_rgb = (r, g, b)
            self.color_display.set_color(r, g, b)
            self.hex_input.setText(f"#{r:02x}{g:02x}{b:02x}".upper())

            self.rgb_group.set_values([r, g, b])
            
            h, l, s = ColorConverter.rgb_to_hls(r, g, b)
            self.hls_group.set_values([h, l, s])
            
        except Exception as e:
            self.show_warning(f"Ошибка преобразования XYZ: {str(e)}")
        finally:
            self.updating = False
    
    def on_hls_changed(self):
        if self.updating:
            return
            
        self.updating = True
        h, l, s = self.hls_group.get_values()
        
        try:
            r, g, b = ColorConverter.hls_to_rgb(h, l, s)

            if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
                self.show_warning("HLS значения приводят к выходу за границы RGB")
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
            
            self.current_rgb = (r, g, b)
            self.color_display.set_color(r, g, b)
            self.hex_input.setText(f"#{r:02x}{g:02x}{b:02x}".upper())
            
            self.rgb_group.set_values([r, g, b])
            
            x, y, z = ColorConverter.rgb_to_xyz(r, g, b)
            self.xyz_group.set_values([x, y, z])
            
        except Exception as e:
            self.show_warning(f"Ошибка преобразования HLS: {str(e)}")
        finally:
            self.updating = False
    
    def on_hex_changed(self):
        if self.updating:
            return
            
        hex_text = self.hex_input.text().strip()
        if hex_text.startswith('#'):
            hex_text = hex_text[1:]
        
        if len(hex_text) == 6:
            try:
                r = int(hex_text[0:2], 16)
                g = int(hex_text[2:4], 16)
                b = int(hex_text[4:6], 16)
                self.set_current_rgb(r, g, b)
            except ValueError:
                pass
    
    def show_color_dialog(self):
        color = QColorDialog.getColor(QColor(*self.current_rgb), self)
        if color.isValid():
            self.set_current_rgb(color.red(), color.green(), color.blue())
    
    def show_warning(self, message):
        self.warning_label.setText(message)
        self.warning_label.setVisible(True)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, self.hide_warning)
    
    def hide_warning(self):
        self.warning_label.setVisible(False)

def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    converter = ColorConverterApp()
    converter.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()