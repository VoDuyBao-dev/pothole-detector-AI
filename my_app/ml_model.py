from openvino.runtime import Core
from django.conf import settings
import os, cv2
import numpy as np
import logging
logger = logging.getLogger('my_app')

# Biến cache model
compiled_model = None
input_layer = None
output_layer = None

def get_model():
    global compiled_model, input_layer, output_layer
    if compiled_model is None:
        model_path = os.path.join(settings.BASE_DIR, 'models', 'pothole_best_openvino_model', 'pothole_best.xml')
        ie = Core()
        model_ov = ie.read_model(model_path)       # đọc và tải cẩu trúc mô hình. chứa mô hình ở dạng IR (Intermediate Representation) gồm câu trúc và trọng số
        compiled_model = ie.compile_model(model=model_ov, device_name="CPU")   # Biên dịch mô hình để chạy trên CPU

        # Lấy input/output
        input_layer = compiled_model.input(0)
        output_layer = compiled_model.output(0)
        logger.debug(f"input_layer: {input_layer}, output_layer: {output_layer}")
    return compiled_model, input_layer, output_layer


# ================== NMS ==================
def nms(boxes, iou_thres=0.45):
    if len(boxes) == 0:
        return []
    boxes = np.array(boxes)
    x1, y1, x2, y2, scores = boxes[:,0], boxes[:,1], boxes[:,2], boxes[:,3], boxes[:,4]
    idxs = scores.argsort()[::-1]
    keep = []

    while len(idxs) > 0:
        i = idxs[0]
        keep.append(i)
        if len(idxs) == 1:
            break

        xx1 = np.maximum(x1[i], x1[idxs[1:]])
        yy1 = np.maximum(y1[i], y1[idxs[1:]])
        xx2 = np.minimum(x2[i], x2[idxs[1:]])
        yy2 = np.minimum(y2[i], y2[idxs[1:]])

        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        union = (x2[i]-x1[i])*(y2[i]-y1[i]) + (x2[idxs[1:]]-x1[idxs[1:]])*(y2[idxs[1:]]-y1[idxs[1:]]) - inter
        iou = inter / (union + 1e-6)

        idxs = idxs[1:][iou <= iou_thres]

    return keep

# ================== HÀM CHẠY INFERENCE ==================
def run_inference(frame, conf_thres=0.25, iou_thres=0.45):
    compiled_model, input_layer, output_layer = get_model()

    # Tiền xử lý
    _, c, h, w = input_layer.shape
    resized = cv2.resize(frame, (w, h))
    resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)  # BGR → RGB
    input_image = resized / 255.0                       # scale về [0,1]
    input_image = input_image.transpose(2, 0, 1)[np.newaxis].astype(np.float32)  
    # logger.debug(f"input_image: {input_image.shape}, dtype: {input_image.dtype}")   #
    # Chạy model
    results = compiled_model([input_image])[output_layer] # shape [1, 5, 8400]
    results = np.squeeze(results).transpose(1, 0)  # (8400, 5)
    logger.debug(f"results shape: {results.shape}")   # 5, 8400   (5 dòng thông tin cho mỗi 8400 ô dự đoán) 
    logger.debug(f"results shape: {results}")   
    # Chuyển thành [5,8400]
    # results = results.transpose(1, 0)
    logger.debug(f"results: {results}")
    # logger.debug(f"frame: {frame}")  

    h_orig, w_orig = frame.shape[:2]
    
    logger.debug(f"h_orig: {h_orig}, w_orig: {w_orig}")      # h_orig: 172, w_orig: 292

    detections_raw = []

    # Duyệt qua từng box
    for x, y, w_box, h_box, conf in results:
        if conf < conf_thres:
            continue

        # Chuyển xywh -> xyxy, scale về ảnh gốc
        x1 = (x - w_box / 2) * w_orig / w
        y1 = (y - h_box / 2) * h_orig / h
        x2 = (x + w_box / 2) * w_orig / w
        y2 = (y + h_box / 2) * h_orig / h

        detections_raw.append([x1, y1, x2, y2, conf])

    # Áp dụng NMS
    keep = nms(detections_raw, iou_thres)

    confidence_TB = 0
    pothole_count = 0

    detections = []
    for i in keep:
        x1, y1, x2, y2, conf = detections_raw[i]
        w_box, h_box = x2 - x1, y2 - y1
        area = max(0, w_box) * max(0, h_box)
        size = f"{int(w_box)}x{int(h_box)}"
        level = "large" if area > 5000 else "medium" if area > 2000 else "small"

        pothole_count += 1
        confidence_TB = (confidence_TB * (pothole_count - 1) + conf) / pothole_count  
        logger.debug(f"Detection: {x1},{y1},{w_box},{h_box}, conf: {conf}, area: {area}, size: {size}, level: {level}")
        detections.append({  # bởi vì có thể có nhiều ổ gà trong một bước ảnh nên sử dụng append
            "x": int(x1),
            "y": int(y1),
            "width": int(w_box),
            "height": int(h_box),
            "confidence": round(float(conf), 4),
            "label": "Pothole",
            "area": int(area),
            "size": size,
            "level": level,
            "confidence_TB": round(float(confidence_TB), 4)
        })
    # trả về danh sách ổ gà phát hiện được
    return detections
