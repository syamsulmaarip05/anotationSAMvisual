import os
import cv2
import math
import streamlit as st

# Import library internal
from src.scanner import scan_all_images, label_from_yolo_structure
from src.yolo_parser import load_yolo_seg_label
from src.visualizer import draw_polygons, bgr_to_rgb

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("VISUALISASI ANOTASI POLYGON - YOLO SEGMENTATION BY SYAMSUL MAARIP")

DEFAULT_DATASET = r"ANOTASI_E8_AUG_822"

# =========================
# CUSTOM CSS
# =========================
st.markdown(
    """
    <style>
    .stApp { background-color: #0f1419; }
    .image-card {
        background: #1a202c;
        border-radius: 10px;
        padding: 8px;
        border: 1px solid #2d3748;
        margin-bottom: 10px;
        text-align: center;
    }
    .file-label {
        font-size: 11px;
        color: #718096;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 5px;
    }
    /* Centering tombol navigasi */
    div[data-testid="stColumn"] > div [data-testid="stVerticalBlock"] {
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# INPUT PATH & SCAN
# =========================
dataset_dir = st.text_input("📂 Path Dataset", value=DEFAULT_DATASET)

if not os.path.exists(dataset_dir):
    st.error("⚠️ Path tidak ditemukan.")
    st.stop()

images_root = os.path.join(dataset_dir, "images")
with st.spinner("🔍 Scanning gambar..."):
    images_data = scan_all_images(images_root)

if not images_data:
    st.error("❌ Tidak ada gambar ditemukan.")
    st.stop()

# =========================
# FILTER SECTION (KEMBALI LENGKAP)
# =========================
st.markdown("### 🔧 Filter & Pengaturan")
f1, f2, f3, f4 = st.columns(4)

with f1:
    split_choice = st.selectbox("Split Dataset", ["(Semua Split)", "train", "val", "test"])
    if split_choice != "(Semua Split)":
        images_data = [d for d in images_data if (os.sep + split_choice + os.sep) in d["img_path"]]

with f2:
    filter_mode = st.selectbox("Status Label", ["Semua", "Hanya label hilang", "Hanya label ada"])
    # Update label info
    for d in images_data:
        d["label_path"] = label_from_yolo_structure(d["img_path"])
        d["label_exists"] = os.path.exists(d["label_path"])
    
    if filter_mode == "Hanya label hilang":
        images_data = [d for d in images_data if not d["label_exists"]]
    elif filter_mode == "Hanya label ada":
        images_data = [d for d in images_data if d["label_exists"]]

with f3:
    class_filter_mode = st.selectbox("Filter Kelas", ["Semua kelas", "Kelas tertentu"])
    selected_class = None
    if class_filter_mode == "Kelas tertentu":
        selected_class = st.number_input("Class ID", min_value=0, value=0, step=1)
        filtered = []
        for d in images_data:
            if d["label_exists"]:
                polys = load_yolo_seg_label(d["label_path"])
                if int(selected_class) in [cls for cls, _ in polys]:
                    filtered.append(d)
        images_data = filtered

with f4:
    search_query = st.text_input("🔎 Cari Nama", placeholder="Ketik nama file...")
    if search_query:
        images_data = [d for d in images_data if search_query.lower() in os.path.basename(d["img_path"]).lower()]

# =========================
# PAGINATION & AUTO-GRID LOGIC
# =========================
st.markdown("---")
# Input hanya jumlah total gambar (selalu genap agar bagi 2 rapi)
per_page = st.number_input("Jumlah Gambar per Halaman", value=12, step=2)

# Otomatis bagi 2 baris
grid_cols_count = max(1, per_page // 2)

total_pages = math.ceil(len(images_data) / per_page)
if "page" not in st.session_state:
    st.session_state.page = 1
st.session_state.page = max(1, min(st.session_state.page, total_pages))

start_idx = (st.session_state.page - 1) * per_page
page_items = images_data[start_idx : start_idx + per_page]

# =========================
# MAIN GALLERY (CENTERED NAV)
# =========================
st.markdown(f'<p style="text-align:center; color:#718096;">Halaman <b>{st.session_state.page}</b> dari {total_pages} ({len(images_data)} total data)</p>', unsafe_allow_html=True)

# Layout: Panah Kiri | Gallery (2 Baris) | Panah Kanan
c_prev, c_main, c_next = st.columns([0.5, 9, 0.5], vertical_alignment="center")

with c_prev:
    if st.button("⬅️", key="nav_prev", use_container_width=True):
        st.session_state.page -= 1
        st.rerun()

with c_next:
    if st.button("➡️", key="nav_next", use_container_width=True):
        st.session_state.page += 1
        st.rerun()

with c_main:
    # Selalu 2 Baris
    for r in range(2):
        cols = st.columns(grid_cols_count)
        for c in range(grid_cols_count):
            idx = r * grid_cols_count + c
            if idx < len(page_items):
                item = page_items[idx]
                with cols[c]:
                    img = cv2.imread(item["img_path"])
                    if img is not None:
                        # Ukuran gambar fix (300px) supaya seragam di grid
                        h, w = img.shape[:2]
                        scale = 300 / max(h, w)
                        img = cv2.resize(img, (int(w * scale), int(h * scale)))
                        
                        polys = load_yolo_seg_label(item["label_path"]) if item["label_exists"] else []
                        if selected_class is not None:
                            polys = [(cls, pts) for cls, pts in polys if cls == int(selected_class)]
                        
                        overlay = draw_polygons(img, polys)
                        
                        st.markdown('<div class="image-card">', unsafe_allow_html=True)
                        st.image(bgr_to_rgb(overlay), use_container_width=True)
                        st.markdown(f'<div class="file-label">{os.path.basename(item["img_path"])}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")