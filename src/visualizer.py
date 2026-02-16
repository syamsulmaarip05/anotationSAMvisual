import cv2


def draw_polygons(image_bgr, polys, thickness=2):
    """
    image_bgr: OpenCV BGR
    polys: list[(cls, pts_norm)]
    """
    h, w = image_bgr.shape[:2]
    out = image_bgr.copy()

    for cls, pts_norm in polys:
        pts_px = pts_norm.copy()
        pts_px[:, 0] *= w
        pts_px[:, 1] *= h
        pts_px = pts_px.astype("int32")

        cv2.polylines(out, [pts_px], isClosed=True, color=(0, 255, 0), thickness=thickness)

        x0, y0 = pts_px[0]
        x0 = max(0, int(x0))
        y0 = max(25, int(y0))

        cv2.putText(
            out,
            f"cls={cls}",
            (x0, y0 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    return out


def bgr_to_rgb(image_bgr):
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
