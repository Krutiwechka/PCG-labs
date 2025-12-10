import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d, Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

class Arrow3D(FancyArrowPatch):
    """Класс для рисования 3D стрелок"""
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return min(zs)

class Letter3DVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Визуализация буквы - Лабораторная работа 6")
        self.root.geometry("1400x900")
        
        # Инициализация данных для буквы "П" (первая буква фамилии "Петров")
        # Каркасная модель буквы П
        self.vertices = np.array([
            # Вершины передней грани (z = 0)
            [0, 0, 0],    # 0
            [0, 10, 0],   # 1
            [2, 10, 0],   # 2
            [2, 2, 0],    # 3
            [8, 2, 0],    # 4
            [8, 10, 0],   # 5
            [10, 10, 0],  # 6
            [10, 0, 0],   # 7
            [8, 0, 0],    # 8
            [8, 8, 0],    # 9
            [2, 8, 0],    # 10
            [2, 0, 0],    # 11
            
            # Вершины задней грани (z = 3)
            [0, 0, 3],    # 12
            [0, 10, 3],   # 13
            [2, 10, 3],   # 14
            [2, 2, 3],    # 15
            [8, 2, 3],    # 16
            [8, 10, 3],   # 17
            [10, 10, 3],  # 18
            [10, 0, 3],   # 19
            [8, 0, 3],    # 20
            [8, 8, 3],    # 21
            [2, 8, 3],    # 22
            [2, 0, 3],    # 23
        ], dtype=float)
        
        # Ребра (соединения между вершинами)
        self.edges = [
            # Передняя грань
            [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8],
            [8, 9], [9, 10], [10, 11], [11, 0], [3, 10], [4, 9], [8, 11],
            
            # Задняя грань
            [12, 13], [13, 14], [14, 15], [15, 16], [16, 17], [17, 18],
            [18, 19], [19, 20], [20, 21], [21, 22], [22, 23], [23, 12],
            [15, 22], [16, 21], [20, 23],
            
            # Соединяющие ребра
            [0, 12], [1, 13], [2, 14], [3, 15], [4, 16], [5, 17],
            [6, 18], [7, 19], [8, 20], [9, 21], [10, 22], [11, 23]
        ]
        
        # Текущие преобразованные вершины
        self.transformed_vertices = self.vertices.copy()
        
        # Матрица преобразования (начинаем с единичной матрицы)
        self.transformation_matrix = np.identity(4)
        
        # Инициализация интерфейса
        self.init_ui()
        
        # Начальная отрисовка
        self.update_plot()
    
    def init_ui(self):
        """Инициализация графического интерфейса"""
        # Основные фреймы
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="nsew")
        
        plot_frame = ttk.Frame(self.root)
        plot_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Настройка весов строк и столбцов
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Панель управления
        ttk.Label(control_frame, text="3D ПРЕОБРАЗОВАНИЯ", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Масштабирование
        ttk.Label(control_frame, text="Масштабирование:", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2, pady=(10, 5), sticky="w")
        
        ttk.Label(control_frame, text="X:").grid(row=2, column=0, sticky="w")
        self.scale_x = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.1, to=3.0, variable=self.scale_x, 
                  orient="horizontal", length=150).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.scale_x).grid(row=2, column=2, padx=5)
        
        ttk.Label(control_frame, text="Y:").grid(row=3, column=0, sticky="w")
        self.scale_y = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.1, to=3.0, variable=self.scale_y, 
                  orient="horizontal", length=150).grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.scale_y).grid(row=3, column=2, padx=5)
        
        ttk.Label(control_frame, text="Z:").grid(row=4, column=0, sticky="w")
        self.scale_z = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.1, to=3.0, variable=self.scale_z, 
                  orient="horizontal", length=150).grid(row=4, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.scale_z).grid(row=4, column=2, padx=5)
        
        ttk.Button(control_frame, text="Применить масштабирование", 
                  command=self.apply_scaling).grid(row=5, column=0, columnspan=3, pady=10)
        
        # Перенос
        ttk.Label(control_frame, text="Перенос:", font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=2, pady=(10, 5), sticky="w")
        
        ttk.Label(control_frame, text="ΔX:").grid(row=7, column=0, sticky="w")
        self.translate_x = tk.DoubleVar(value=0.0)
        ttk.Scale(control_frame, from_=-10, to=10, variable=self.translate_x, 
                  orient="horizontal", length=150).grid(row=7, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.translate_x).grid(row=7, column=2, padx=5)
        
        ttk.Label(control_frame, text="ΔY:").grid(row=8, column=0, sticky="w")
        self.translate_y = tk.DoubleVar(value=0.0)
        ttk.Scale(control_frame, from_=-10, to=10, variable=self.translate_y, 
                  orient="horizontal", length=150).grid(row=8, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.translate_y).grid(row=8, column=2, padx=5)
        
        ttk.Label(control_frame, text="ΔZ:").grid(row=9, column=0, sticky="w")
        self.translate_z = tk.DoubleVar(value=0.0)
        ttk.Scale(control_frame, from_=-10, to=10, variable=self.translate_z, 
                  orient="horizontal", length=150).grid(row=9, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.translate_z).grid(row=9, column=2, padx=5)
        
        ttk.Button(control_frame, text="Применить перенос", 
                  command=self.apply_translation).grid(row=10, column=0, columnspan=3, pady=10)
        
        # Вращение
        ttk.Label(control_frame, text="Вращение:", font=("Arial", 10, "bold")).grid(row=11, column=0, columnspan=2, pady=(10, 5), sticky="w")
        
        ttk.Label(control_frame, text="Угол (°):").grid(row=12, column=0, sticky="w")
        self.rotate_angle = tk.DoubleVar(value=0.0)
        ttk.Scale(control_frame, from_=-180, to=180, variable=self.rotate_angle, 
                  orient="horizontal", length=150).grid(row=12, column=1, padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.rotate_angle).grid(row=12, column=2, padx=5)
        
        ttk.Label(control_frame, text="Ось вращения:").grid(row=13, column=0, sticky="w")
        self.rotation_axis = tk.StringVar(value="X")
        axis_combo = ttk.Combobox(control_frame, textvariable=self.rotation_axis, 
                                  values=["X", "Y", "Z", "Произвольная"], state="readonly", width=15)
        axis_combo.grid(row=13, column=1, columnspan=2, pady=5)
        
        # Параметры произвольной оси
        ttk.Label(control_frame, text="Произвольная ось:").grid(row=14, column=0, columnspan=3, pady=(10, 5), sticky="w")
        
        ttk.Label(control_frame, text="X1,Y1,Z1:").grid(row=15, column=0, sticky="w")
        self.axis_x1 = tk.DoubleVar(value=0.0)
        self.axis_y1 = tk.DoubleVar(value=0.0)
        self.axis_z1 = tk.DoubleVar(value=0.0)
        ttk.Entry(control_frame, textvariable=self.axis_x1, width=5).grid(row=15, column=1)
        ttk.Entry(control_frame, textvariable=self.axis_y1, width=5).grid(row=15, column=2)
        ttk.Entry(control_frame, textvariable=self.axis_z1, width=5).grid(row=15, column=3)
        
        ttk.Label(control_frame, text="X2,Y2,Z2:").grid(row=16, column=0, sticky="w")
        self.axis_x2 = tk.DoubleVar(value=1.0)
        self.axis_y2 = tk.DoubleVar(value=1.0)
        self.axis_z2 = tk.DoubleVar(value=1.0)
        ttk.Entry(control_frame, textvariable=self.axis_x2, width=5).grid(row=16, column=1)
        ttk.Entry(control_frame, textvariable=self.axis_y2, width=5).grid(row=16, column=2)
        ttk.Entry(control_frame, textvariable=self.axis_z2, width=5).grid(row=16, column=3)
        
        ttk.Button(control_frame, text="Применить вращение", 
                  command=self.apply_rotation).grid(row=17, column=0, columnspan=4, pady=10)
        
        # Кнопки управления
        ttk.Button(control_frame, text="Сбросить преобразования", 
                  command=self.reset_transformations).grid(row=18, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Показать матрицу преобразования", 
                  command=self.show_transformation_matrix).grid(row=19, column=0, columnspan=2, pady=5)
        
        # Область для графиков
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Информационная панель
        info_frame = ttk.Frame(self.root)
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ttk.Label(info_frame, text="Лабораторная работа 6a, 6b, 6c: 3D визуализация и преобразования", 
                 font=("Arial", 10, "bold")).pack()
        ttk.Label(info_frame, text="Буква 'П' (каркасная модель)").pack()
        ttk.Label(info_frame, text="Управление: используйте слайдеры для изменения параметров преобразований").pack()
    
    def apply_scaling(self):
        """Применение масштабирования"""
        sx, sy, sz = self.scale_x.get(), self.scale_y.get(), self.scale_z.get()
        
        # Создание матрицы масштабирования
        scale_matrix = np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ])
        
        # Применение преобразования
        self.apply_transformation(scale_matrix, f"Масштабирование: Sx={sx:.2f}, Sy={sy:.2f}, Sz={sz:.2f}")
        
        # Сброс слайдеров
        self.scale_x.set(1.0)
        self.scale_y.set(1.0)
        self.scale_z.set(1.0)
    
    def apply_translation(self):
        """Применение переноса"""
        tx, ty, tz = self.translate_x.get(), self.translate_y.get(), self.translate_z.get()
        
        # Создание матрицы переноса
        translation_matrix = np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])
        
        # Применение преобразования
        self.apply_transformation(translation_matrix, f"Перенос: Tx={tx:.2f}, Ty={ty:.2f}, Tz={tz:.2f}")
        
        # Сброс слайдеров
        self.translate_x.set(0.0)
        self.translate_y.set(0.0)
        self.translate_z.set(0.0)
    
    def apply_rotation(self):
        """Применение вращения"""
        angle = np.radians(self.rotate_angle.get())
        axis = self.rotation_axis.get()
        
        if axis == "X":
            # Вращение вокруг оси X
            rotation_matrix = np.array([
                [1, 0, 0, 0],
                [0, np.cos(angle), -np.sin(angle), 0],
                [0, np.sin(angle), np.cos(angle), 0],
                [0, 0, 0, 1]
            ])
            description = f"Вращение вокруг оси X на {self.rotate_angle.get():.1f}°"
            
        elif axis == "Y":
            # Вращение вокруг оси Y
            rotation_matrix = np.array([
                [np.cos(angle), 0, np.sin(angle), 0],
                [0, 1, 0, 0],
                [-np.sin(angle), 0, np.cos(angle), 0],
                [0, 0, 0, 1]
            ])
            description = f"Вращение вокруг оси Y на {self.rotate_angle.get():.1f}°"
            
        elif axis == "Z":
            # Вращение вокруг оси Z
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle), 0, 0],
                [np.sin(angle), np.cos(angle), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
            description = f"Вращение вокруг оси Z на {self.rotate_angle.get():.1f}°"
            
        else:
            # Вращение вокруг произвольной оси
            x1, y1, z1 = self.axis_x1.get(), self.axis_y1.get(), self.axis_z1.get()
            x2, y2, z2 = self.axis_x2.get(), self.axis_y2.get(), self.axis_z2.get()
            
            # Вектор оси
            v = np.array([x2 - x1, y2 - y1, z2 - z1])
            v = v / np.linalg.norm(v)  # Нормализация
            
            # Матрица вращения вокруг произвольной оси (формула Родрига)
            c = np.cos(angle)
            s = np.sin(angle)
            t = 1 - c
            
            x, y, z = v
            
            rotation_matrix = np.array([
                [t*x*x + c, t*x*y - s*z, t*x*z + s*y, 0],
                [t*x*y + s*z, t*y*y + c, t*y*z - s*x, 0],
                [t*x*z - s*y, t*y*z + s*x, t*z*z + c, 0],
                [0, 0, 0, 1]
            ])
            
            description = f"Вращение вокруг оси ({x1:.1f},{y1:.1f},{z1:.1f})-({x2:.1f},{y2:.1f},{z2:.1f}) на {self.rotate_angle.get():.1f}°"
        
        # Применение преобразования
        self.apply_transformation(rotation_matrix, description)
        
        # Сброс слайдера угла
        self.rotate_angle.set(0.0)
    
    def apply_transformation(self, transformation_matrix, description):
        """Применение матрицы преобразования к вершинам"""
        # Обновление общей матрицы преобразования
        self.transformation_matrix = transformation_matrix @ self.transformation_matrix
        
        # Преобразование вершин
        for i in range(len(self.transformed_vertices)):
            vertex = self.transformed_vertices[i]
            # Преобразование в однородные координаты
            homogeneous_vertex = np.array([vertex[0], vertex[1], vertex[2], 1])
            # Применение преобразования
            transformed_vertex = transformation_matrix @ homogeneous_vertex
            # Обратное преобразование из однородных координат
            self.transformed_vertices[i] = transformed_vertex[:3]
        
        # Обновление графика
        self.update_plot()
        
        # Вывод информации о преобразовании
        print(f"Применено: {description}")
    
    def reset_transformations(self):
        """Сброс всех преобразований"""
        self.transformed_vertices = self.vertices.copy()
        self.transformation_matrix = np.identity(4)
        self.update_plot()
        print("Все преобразования сброшены")
    
    def show_transformation_matrix(self):
        """Отображение текущей матрицы преобразования"""
        matrix_text = "Текущая матрица преобразования:\n\n"
        for row in self.transformation_matrix:
            matrix_text += "  ".join([f"{val:8.3f}" for val in row]) + "\n"
        
        messagebox.showinfo("Матрица преобразования", matrix_text)
    
    def create_3d_plot(self, ax, vertices, edges, title, elevation=20, azimuth=45):
        """Создание 3D графика"""
        ax.clear()
        
        # Рисуем ребра
        for edge in edges:
            x = [vertices[edge[0]][0], vertices[edge[1]][0]]
            y = [vertices[edge[0]][1], vertices[edge[1]][1]]
            z = [vertices[edge[0]][2], vertices[edge[1]][2]]
            ax.plot(x, y, z, 'b-', linewidth=2)
        
        # Рисуем вершины
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                  c='r', marker='o', s=50, depthshade=True)
        
        # Настройка осей
        ax.set_xlabel('Ось X')
        ax.set_ylabel('Ось Y')
        ax.set_zlabel('Ось Z')
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Установка лимитов осей
        max_range = max(np.ptp(vertices[:, 0]), np.ptp(vertices[:, 1]), np.ptp(vertices[:, 2]))
        mid_x = (np.max(vertices[:, 0]) + np.min(vertices[:, 0])) / 2
        mid_y = (np.max(vertices[:, 1]) + np.min(vertices[:, 1])) / 2
        mid_z = (np.max(vertices[:, 2]) + np.min(vertices[:, 2])) / 2
        
        ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
        ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
        ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
        
        # Рисуем оси координат
        axis_length = max_range * 0.5
        origin = [mid_x - max_range/2, mid_y - max_range/2, mid_z - max_range/2]
        
        # Ось X (красная)
        ax.quiver(origin[0], origin[1], origin[2], 
                 axis_length, 0, 0, color='r', arrow_length_ratio=0.1, linewidth=2)
        # Ось Y (зеленая)
        ax.quiver(origin[0], origin[1], origin[2], 
                 0, axis_length, 0, color='g', arrow_length_ratio=0.1, linewidth=2)
        # Ось Z (синяя)
        ax.quiver(origin[0], origin[1], origin[2], 
                 0, 0, axis_length, color='b', arrow_length_ratio=0.1, linewidth=2)
        
        # Подписи осей
        ax.text(origin[0] + axis_length*1.1, origin[1], origin[2], 'X', color='r', fontsize=12, fontweight='bold')
        ax.text(origin[0], origin[1] + axis_length*1.1, origin[2], 'Y', color='g', fontsize=12, fontweight='bold')
        ax.text(origin[0], origin[1], origin[2] + axis_length*1.1, 'Z', color='b', fontsize=12, fontweight='bold')
        
        # Установка угла обзора
        ax.view_init(elev=elevation, azim=azimuth)
    
    def create_projection_plot(self, ax, vertices, edges, title, projection_plane):
        """Создание графика проекции на указанную плоскость"""
        ax.clear()
        
        # Выбор проекции
        if projection_plane == 'xy':
            # Проекция на плоскость Oxy (z=0)
            proj_vertices = vertices.copy()
            proj_vertices[:, 2] = 0
            x_label, y_label = 'X', 'Y'
            
        elif projection_plane == 'xz':
            # Проекция на плоскость Oxz (y=0)
            proj_vertices = vertices.copy()
            proj_vertices[:, 1] = 0
            x_label, y_label = 'X', 'Z'
            
        elif projection_plane == 'yz':
            # Проекция на плоскость Oyz (x=0)
            proj_vertices = vertices.copy()
            proj_vertices[:, 0] = 0
            x_label, y_label = 'Y', 'Z'
        
        # Рисуем ребра
        for edge in edges:
            x = [proj_vertices[edge[0]][0], proj_vertices[edge[1]][0]]
            y = [proj_vertices[edge[0]][1], proj_vertices[edge[1]][1]]
            ax.plot(x, y, 'b-', linewidth=2)
        
        # Рисуем вершины
        ax.scatter(proj_vertices[:, 0], proj_vertices[:, 1], 
                  c='r', marker='o', s=40)
        
        # Настройка осей
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')
        
        # Установка лимитов осей
        max_range_x = np.ptp(proj_vertices[:, 0])
        max_range_y = np.ptp(proj_vertices[:, 1])
        max_range = max(max_range_x, max_range_y)
        
        mid_x = (np.max(proj_vertices[:, 0]) + np.min(proj_vertices[:, 0])) / 2
        mid_y = (np.max(proj_vertices[:, 1]) + np.min(proj_vertices[:, 1])) / 2
        
        ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
        ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
        
        # Рисуем оси координат
        axis_length = max_range * 0.4
        origin = [mid_x - max_range/2, mid_y - max_range/2]
        
        # Горизонтальная ось
        ax.arrow(origin[0], origin[1], axis_length, 0, 
                head_width=max_range*0.03, head_length=max_range*0.03, 
                fc='r', ec='r', linewidth=2)
        # Вертикальная ось
        ax.arrow(origin[0], origin[1], 0, axis_length, 
                head_width=max_range*0.03, head_length=max_range*0.03, 
                fc='g', ec='g', linewidth=2)
        
        # Подписи осей
        ax.text(origin[0] + axis_length*1.1, origin[1], x_label, 
               color='r', fontsize=10, fontweight='bold')
        ax.text(origin[0], origin[1] + axis_length*1.1, y_label, 
               color='g', fontsize=10, fontweight='bold')
    
    def update_plot(self):
        """Обновление всех графиков"""
        self.figure.clear()
        
        # Основной 3D график
        ax1 = self.figure.add_subplot(221, projection='3d')
        self.create_3d_plot(ax1, self.transformed_vertices, self.edges, 
                           "3D модель буквы 'П'", elevation=25, azimuth=45)
        
        # Ортографические проекции
        ax2 = self.figure.add_subplot(222)
        self.create_projection_plot(ax2, self.transformed_vertices, self.edges, 
                                   "Проекция на плоскость OXY", 'xy')
        
        ax3 = self.figure.add_subplot(223)
        self.create_projection_plot(ax3, self.transformed_vertices, self.edges, 
                                   "Проекция на плоскость OXZ", 'xz')
        
        ax4 = self.figure.add_subplot(224)
        self.create_projection_plot(ax4, self.transformed_vertices, self.edges, 
                                   "Проекция на плоскость OYZ", 'yz')
        
        # Настройка общего заголовка и отступов
        self.figure.suptitle("Лабораторная работа 6: 3D Визуализация и преобразования", 
                            fontsize=14, fontweight='bold')
        self.figure.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Обновление canvas
        self.canvas.draw()

def main():
    """Основная функция"""
    root = tk.Tk()
    app = Letter3DVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
