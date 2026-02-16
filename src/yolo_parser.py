import os
import numpy as np


def load_yolo_seg_label(label_path: str):
    """
    Format YOLO-Seg:
    class x1 y1 x2 y2 x3 y3 ...

    Return:
    polys: list[(cls, pts_norm)]
    """
    polys = []
    if not label_path or not os.path.exists(label_path):
        return polys

    with open(label_path, "r") as f:
        lines = f.read().strip().splitlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 3:
            continue

        cls = int(float(parts[0]))
        coords = list(map(float, parts[1:]))

        # minimal polygon 3 titik = 6 angka
        if len(coords) < 6:
            continue

        try:
            pts = np.array(coords, dtype=np.float32).reshape(-1, 2)
        except Exception:
            continue

        polys.append((cls, pts))

    return polys
