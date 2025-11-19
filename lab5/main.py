import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Button, filedialog, messagebox

def liang_barsky_clip(x1, y1, x2, y2, clip_rect):
    xmin, ymin, xmax, ymax = clip_rect
    
    dx = x2 - x1
    dy = y2 - y1
    
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    
    u1 = 0.0
    u2 = 1.0
    
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None
        else:
            u = q[i] / p[i]
            if p[i] < 0:
                if u > u1:
                    u1 = u
            else:
                if u < u2:
                    u2 = u
    
    if u1 > u2:
        return None
    
    x1_clip = x1 + u1 * dx
    y1_clip = y1 + u1 * dy
    x2_clip = x1 + u2 * dx
    y2_clip = y1 + u2 * dy
    
    return [(x1_clip, y1_clip), (x2_clip, y2_clip)]


def polygon_clip(x1, y1, x2, y2, clip_polygon):
    n = len(clip_polygon)
    tE = 0.0
    tL = 1.0
    
    D = (x2 - x1, y2 - y1)
    
    for i in range(n):
        A = clip_polygon[i]
        B = clip_polygon[(i + 1) % n]
        
        edge_vec = (B[0] - A[0], B[1] - A[1])
        normal = (-edge_vec[1], edge_vec[0])
        
        w = (x1 - A[0], y1 - A[1])
        
        D_dot_n = D[0] * normal[0] + D[1] * normal[1]
        w_dot_n = w[0] * normal[0] + w[1] * normal[1]
        
        if D_dot_n == 0:
            if w_dot_n < 0:
                return None
            else:
                continue
        
        t = -w_dot_n / D_dot_n
        
        if D_dot_n > 0:
            if t > tE:
                tE = t
        else:
            if t < tL:
                tL = t
        
        if tE > tL:
            return None
    
    if tE <= tL and 0 <= tE <= 1 and 0 <= tL <= 1:
        x1_clip = x1 + tE * D[0]
        y1_clip = y1 + tE * D[1]
        x2_clip = x1 + tL * D[0]
        y2_clip = y1 + tL * D[1]
        return [(x1_clip, y1_clip), (x2_clip, y2_clip)]
    
    return None


def plot_segments_with_rect_clipping(segments, clip_rect):
    fig, ax = plt.subplots()

    xmin, ymin, xmax, ymax = clip_rect
    rect = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]

    ax.plot(*zip(*rect), color='b', linewidth=2, label='Clip Rectangle')

    for (x1, y1), (x2, y2) in segments:
        ax.plot([x1, x2], [y1, y2], color='r', linestyle='--', label='Original Segment')
        clipped = liang_barsky_clip(x1, y1, x2, y2, clip_rect)
        if clipped:
            ax.plot([clipped[0][0], clipped[1][0]], [clipped[0][1], clipped[1][1]],
                    color='g', linewidth=2, label='Clipped Segment')

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    
    ax.set_title("Segment Clipping with Rectangle (Liang-Barsky)")
    ax.set_aspect('equal')
    plt.show()


def plot_segments_with_polygon_clipping(segments, clip_polygon):
    fig, ax = plt.subplots()

    closed_polygon = clip_polygon + [clip_polygon[0]]

    ax.plot(*zip(*closed_polygon), color='b', linewidth=2, label='Clip Polygon')
    ax.fill(*zip(*clip_polygon), alpha=0.2, color='blue')

    for (x1, y1), (x2, y2) in segments:
        ax.plot([x1, x2], [y1, y2], color='r', linestyle='--', label='Original Segment')
        clipped = polygon_clip(x1, y1, x2, y2, clip_polygon)
        if clipped:
            ax.plot([clipped[0][0], clipped[1][0]], [clipped[0][1], clipped[1][1]],
                    color='g', linewidth=2, label='Clipped Segment')

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    
    ax.set_title("Segment Clipping with Polygon")
    ax.set_aspect('equal')
    plt.show()


def read_segments_rect(file_path):
    with open(file_path, 'r') as f:
        n = int(f.readline().strip())
        segments = [tuple(map(float, f.readline().strip().split())) for _ in range(n)]
        clip_rect = tuple(map(float, f.readline().strip().split()))
    return [(segments[i][:2], segments[i][2:]) for i in range(n)], clip_rect


def read_segments_polygon(file_path):
    with open(file_path, 'r') as f:
        n_segments = int(f.readline().strip())
        segments = []
        for _ in range(n_segments):
            coords = list(map(float, f.readline().strip().split()))
            segments.append(((coords[0], coords[1]), (coords[2], coords[3])))
        
        n_polygon = int(f.readline().strip())
        clip_polygon = [tuple(map(float, f.readline().strip().split())) for _ in range(n_polygon)]
    
    return segments, clip_polygon


def open_file_for_rect_clipping():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            segments, clip_rect = read_segments_rect(file_path)
            plot_segments_with_rect_clipping(segments, clip_rect)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")


def open_file_for_polygon_clipping():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            segments, clip_polygon = read_segments_polygon(file_path)
            plot_segments_with_polygon_clipping(segments, clip_polygon)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")


def main_gui():
    root = Tk()
    root.title("Segment Clipping Algorithms")
    root.geometry("350x120")

    Button(root, text="Load Segments (Rectangle Clipping)", 
           command=open_file_for_rect_clipping).pack(pady=10)
    Button(root, text="Load Segments (Polygon Clipping)", 
           command=open_file_for_polygon_clipping).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main_gui()
