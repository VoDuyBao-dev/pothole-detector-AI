from django.shortcuts import render
import cv2
import torch
from ultralytics import YOLO
import numpy as np
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os, tempfile, math
from django.conf import settings
from django.utils.timezone import now
from .models import * 

def dashboard(request):
    return render(request, 'my_app/dashboard.html')

def sign_up_and_sign_in(request):
    return render(request, 'my_app/sign_up_and_sign_in.html')

def map(request):
    return render(request, 'my_app/map.html')

def history(request):
    return render(request, 'my_app/history.html')

def account_management(request):
    return render(request, 'my_app/account_management.html')

def model_training(request):
    return render(request, 'my_app/model_training.html')





# Define model path relative to project root
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'pothole_best.pt')

# Ensure model directory exists
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

try:
    model = YOLO(MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(
        f"Model file not found at {MODEL_PATH}. "
        "Please ensure the model file 'pothole_best.pt' is placed in the 'models' directory"
    )

# ================== HÀM HỖ TRỢ ==================
def haversine(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 toạ độ GPS (mét)"""
    R = 6371000  # bán kính Trái Đất (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_or_create_pothole(user, lat, lon, confidence, size, area):
    """Tìm ổ gà gần đó, nếu chưa có thì tạo mới"""
    threshold = 5  # mét, bán kính gom cụm
    nearby = None

    for pothole in Pothole.objects.all():
        if haversine(lat, lon, pothole.latitude, pothole.longitude) < threshold:
            nearby = pothole
            break

    if nearby:
        # Cập nhật thông tin tổng hợp
        nearby.detections_count += 1
        nearby.confidence_avg = (nearby.confidence_avg * (nearby.detections_count - 1) + confidence) / nearby.detections_count
        nearby.save()
    else:
        # Tạo ổ gà mới
        nearby = Pothole.objects.create(
            latitude=lat,
            longitude=lon,
            first_detected_by=user if user.is_authenticated else None,
            confidence_avg=confidence,
            detections_count=1
        )

    # Luôn lưu detection mới
    PotholeDetection.objects.create(
        pothole=nearby,
        user=user if user.is_authenticated else None,
        latitude=lat,
        longitude=lon,
        size=size,
        confidence=confidence,
        area=area
    )

    return nearby

def draw_boxes(frame, results, user=None, gps=None):
    results = results[0]
    for box in results.boxes:
        # Toạ độ khung ảnh
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = f"{results.names[cls]} {conf:.2f}"

        # Vẽ lên frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 100, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 2)

        # Tính area (diện tích bbox)
        area = (x2 - x1) * (y2 - y1)
        size = "large" if area > 5000 else "small"

        # Nếu có GPS thì lưu DB
        if gps:
            lat, lon = gps
            get_or_create_pothole(user, lat, lon, conf, size, area)

    return frame
# ================== CAMERA STREAM ==================
def generate_camera(request):
    cap = cv2.VideoCapture(0)
    gps = request.GET.get("gps")  # ví dụ truyền từ frontend ?gps=10.762622,106.660172
    gps = tuple(map(float, gps.split(","))) if gps else None

    while True:
        success, frame = cap.read()
        if not success:
            break
        results = model(frame)
        frame = draw_boxes(frame, results, user=request.user, gps=gps)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def camera_feed(request):
    return StreamingHttpResponse(generate_camera(request),
                                 content_type="multipart/x-mixed-replace; boundary=frame")


# ===============  VIDEO UPLOAD  ===============
def generate_video(path):
    cap = cv2.VideoCapture(path)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        results = model(frame)
        frame = draw_boxes(frame, results)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@csrf_exempt
def video_upload(request):
    if request.method == "POST" and request.FILES.get("video"):
        file = request.FILES["video"]
        # Lưu video tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            path = tmp.name
        return StreamingHttpResponse(generate_video(path),
                                     content_type="multipart/x-mixed-replace; boundary=frame")
    return JsonResponse({"error": "No video uploaded"})


# ================== IMAGE DETECTION ==================
@csrf_exempt
def detect_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        img = cv2.imdecode(np.frombuffer(request.FILES["image"].read(), np.uint8), cv2.IMREAD_COLOR)
        results = model(img)

        gps = request.POST.get("gps")
        gps = tuple(map(float, gps.split(","))) if gps else None

        img = draw_boxes(img, results, user=request.user, gps=gps)

        _, buffer = cv2.imencode(".jpg", img)
        return JsonResponse({"image": buffer.tobytes().hex()})
    return JsonResponse({"error": "No image uploaded"})


def live_detection(request):
    return render(request, 'my_app/live_detection.html')
