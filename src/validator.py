import os
import pandas as pd
from datetime import datetime


def ensure_output_dir(output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)


def append_validation_row(csv_path, row_dict):
    """
    Append 1 row ke CSV hasil validasi.
    Kalau file belum ada, otomatis bikin header.
    """
    df_new = pd.DataFrame([row_dict])

    if not os.path.exists(csv_path):
        df_new.to_csv(csv_path, index=False)
    else:
        df_new.to_csv(csv_path, mode="a", header=False, index=False)


def make_validation_row(img_path, label_path, label_exists, polygon_count, status):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "img_path": img_path,
        "label_path": label_path if label_path else "",
        "label_exists": bool(label_exists),
        "polygon_count": int(polygon_count),
        "status": status
    }
