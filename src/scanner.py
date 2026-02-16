import os

IMG_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def scan_all_images(root_dir: str):
    results = []
    if not os.path.exists(root_dir):
        return results

    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(IMG_EXTS):
                img_path = os.path.join(root, f)
                results.append({
                    "img_name": f,
                    "img_path": img_path,
                    "folder": root
                })

    results.sort(key=lambda x: x["img_path"].lower())
    return results


def label_from_yolo_structure(img_path: str):

    # handle Windows path
    if "\\images\\" in img_path:
        label_path = img_path.replace("\\images\\", "\\labels\\")
    else:
        # handle Linux/Mac path
        label_path = img_path.replace("/images/", "/labels/")

    base, _ = os.path.splitext(label_path)
    return base + ".txt"
