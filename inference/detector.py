# inference/detector.py
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

# Load model MỘT LẦN khi import (tối ưu hiệu năng)
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "pothole_best.pt"
model = YOLO(str(MODEL_PATH))

def detect_image(input_path: str, save_vis: bool = True, conf: float = 0.25, iou: float = 0.45):
    """
    Chạy detection trên 1 ảnh.
    Trả về:
      - boxes: list[dict] = [{x1,y1,x2,y2,conf,cls}]
      - vis_path: đường dẫn ảnh vẽ bbox (nếu save_vis=True)
    """ 
    results = model.predict(
        source=input_path,
        conf=conf,
        iou=iou,
        verbose=False
    )

    r = results[0]
    boxes_out = []
    if r.boxes is not None and len(r.boxes) > 0:
        for b in r.boxes:
            xyxy = b.xyxy[0].tolist()
            confv = float(b.conf[0].item())
            clsid = int(b.cls[0].item())
            boxes_out.append({
                "x1": float(xyxy[0]), "y1": float(xyxy[1]),
                "x2": float(xyxy[2]), "y2": float(xyxy[3]),
                "conf": confv, "cls": clsid
            })

    vis_path = None
    if save_vis:
        # r.plot() trả ảnh (ndarray BGR) đã vẽ bbox
        plotted = r.plot()
        vis_path = str(Path(input_path).with_name(Path(input_path).stem + "_det.jpg"))
        cv2.imwrite(vis_path, plotted)

    return boxes_out, vis_path



model = YOLO(MODEL_PATH)

def detect_image2(image_path):
    results = model(image_path)
    return results