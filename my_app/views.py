from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
import cv2, base64, json, os
# import torch
from ultralytics import YOLO
import numpy as np
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os, tempfile, math
from django.conf import settings
from django.utils import timezone
from .models import * 
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout 

import logging
logger = logging.getLogger('my_app')


def dashboard(request):
    return render(request, 'my_app/index.html')
 
def account_management(request):
    return render(request, 'my_app/admin/account.html')




def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        logger.debug(f"Registering user with email: {email}")
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'my_app/admin/account.html', {'error': 'Email không hợp lệ.'})

        
        if User.objects.filter(username=email).exists():
            return render(request, 'my_app/admin/account.html', {'error': 'Email đã tồn tại.'})
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
# tạo 1 đối tượng tương ứng bên UserProfile với role mặc định là 'user'
        UserProfile.objects.create(user=user, role='user')

        return render(request, 'my_app/admin/account.html', {'success': 'Tài khoản đã được tạo thành công.'})
    return redirect('account_management')


def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email không hợp lệ.'})
        # logger.debug(f"email của bạn là: {email}")
        user = User.objects.filter(username=email).first()
        logger.debug(f"người dùng của bạn là: {user}")
        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email hoặc mật khẩu không đúng.'})
        
    return render(request, 'my_app/sign_up_and_sign_in.html')


def signout(request):
    logout(request)
    return redirect('signin')



def _is_admin(user):
    try:
        return user.profile.role == "admin"
    except UserProfile.DoesNotExist:
        return False


@login_required
def history(request):
    """
    - Admin: danh sách Pothole (tổng quan).
    - User: danh sách PotholeDetection của chính mình, kèm ảnh và avg confidence của ổ gà.
    """
    if _is_admin(request.user):
        potholes = (
            Pothole.objects
            .select_related("first_detected_by")
            .order_by("id")  # Sắp xếp tăng dần theo id
        )
        # Lấy thông tin detection của từng pothole
        # detections = (
        #     PotholeDetection.objects
        #     .select_related("user", "pothole")
        #     .values('latitude', 'longitude')
        #     .order_by("-detected_at")
        # )
        return render(request, "my_app/history.html", {
            "is_admin": True,
            "potholes": potholes,
            # "detections": detections    
        })
    else:
        detections = (
            PotholeDetection.objects
            .filter(user=request.user)
            .select_related("pothole")            # để lấy pothole.confidence_avg
            .prefetch_related("images")           # để hiển thị ảnh nhanh
            .order_by("detected_at")
        )
        return render(request, "my_app/history.html", {
            "is_admin": False,
            "potholes": detections,               # template đang dùng biến 'potholes'
        })


@login_required
@user_passes_test(_is_admin)   # chặn user thường
def pothole_detail(request, pothole_id):
    pothole = get_object_or_404(Pothole, id=pothole_id)
    detections = PotholeDetection.objects.filter(pothole=pothole)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = []
        for d in detections:
            img_url = d.images.first().image.url if d.images.exists() else ""
            data.append({
                "pothole_id": d.pothole.id,
                "image_url": img_url,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "area": d.area,
                "size": d.size,
                "level": d.level,
                "confidence": float(d.confidence),
                "created_at": d.detected_at.strftime("%d/%m/%Y %H:%M"),
            })
        return JsonResponse(data, safe=False)

    # fallback render page
    return render(request, "my_app/history.html", {"pothole": pothole})

def map(request):
    pothole_id = request.GET.get("pothole_id")
    highlighted = None

    if pothole_id:
        highlighted = get_object_or_404(Pothole, id=pothole_id)

    potholes = Pothole.objects.all()
    return render(request, "my_app/map.html", {
        "potholes": potholes,
        "highlighted": highlighted
    })




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

# hiển thị thông báo ở một góc của giao diện
def phatHienOGa(request):
    messages.success(request, "Thêm ổ gà mới vào CSDL thành công!")
def gpsWarning(request):
    messages.error(request, "⚠️ Không có GPS, không thể lưu vị trí ổ gà!")

# ================== HÀM HỖ TRỢ ==================
def haversine(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 toạ độ GPS (mét)"""
    R = 6371000  # bán kính Trái Đất (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    logger.debug(f"Haversine distance: {distance}")
    return distance

# Tìm ổ gà gần đó, nếu chưa có thì tạo mới 
@login_required
def get_or_create_pothole(request, user, lat, lon, confidence, size, area, level):
    threshold = 3  # mét, bán kính gom cụm
    nearby = None

    # 🔹 Lọc trong phạm vi nhỏ quanh GPS trước rồi mới tính haversine(khoảng cách giữa 2 tọa độ) (tăng hiệu năng)
    delta = 0.0001  # ~11m
    candidates = Pothole.objects.filter(
        latitude__range=(lat - delta, lat + delta),
        longitude__range=(lon - delta, lon + delta)
    )

    for pothole in candidates:
        if haversine(lat, lon, pothole.latitude, pothole.longitude) < threshold:
            nearby = pothole
            break
    # 🔹 Nếu vẫn chưa có thì tạo mới
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
            first_detected_by=user,
            confidence_avg=confidence,
            detections_count=1
        )
        phatHienOGa(request)
        logger.debug(f"Haversine distance: {nearby}")
    # Luôn lưu detection mới
    tmp = PotholeDetection.objects.create(
        pothole=nearby,
        user=user,
        latitude=lat,
        longitude=lon,
        size=size,
        confidence=confidence,
        area=area,
        level=level 
    )
    logger.debug(f"Haversine distance: {tmp}")

    return nearby

def live_detection_page(request):
    return render(request, "my_app/live_detection.html")


@csrf_exempt
@login_required
def live_detection(request):
    """
    Nhận POST multipart/form-data:
      - 'frame': file ảnh JPEG (blob)
      - optional 'lat', 'lon' (strings)
    Trả JSON:
      { "detections": [ { x, y, width, height, confidence, label, area, size }, ... ] }
    Nếu lat/lon được gửi và có detections thì lưu vào DB bằng get_or_create_pothole(...)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # 1) Lấy frame bytes: hỗ trợ multipart/form-data (request.FILES['frame'])
        img_bytes = None
        if request.FILES.get('frame'):
            img_bytes = request.FILES['frame'].read()
        else:
            # nếu client gửi JSON base64 (không dùng trong JS hiện tại), cố parse
            try:
                body = json.loads(request.body.decode('utf-8') or "{}")
                frame_b64 = body.get('frame') or body.get('image')
                if frame_b64:
                    if ',' in frame_b64:
                        frame_b64 = frame_b64.split(',', 1)[1]
                    img_bytes = base64.b64decode(frame_b64)
            except Exception:
                img_bytes = None

        if not img_bytes:
            return JsonResponse({"error": "No frame received"}, status=400)

        # Parse GPS (fallback: request.POST for form-data)
        lat = request.POST.get('lat') or (body.get('lat') if 'body' in locals() else None)
        lon = request.POST.get('lon') or (body.get('lon') if 'body' in locals() else None)
        gps = None
        if lat is not None and lon is not None:
            try:
                gps = (float(lat), float(lon))
            except Exception:
                gps = None
                gpsWarning(request)

        # Decode image
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return JsonResponse({"error": "Invalid image"}, status=400)

        # Run model (tùy bạn điều chỉnh imgsz/conf để trade speed/accuracy)
        # results = model(frame, imgsz=640, conf=0.25)  # nếu model hỗ trợ tham số
        results = model(frame)  # dùng mặc định

        detections = []
        # results có dạng list, lấy results[0]
        res0 = results[0]
        names = getattr(res0, "names", None) or {}

        for box in res0.boxes:
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            conf = float(box.conf[0])  # 0..1
            cls = int(box.cls[0])
            label = names.get(cls, str(cls))
            w = x2 - x1
            h = y2 - y1
            area = int(max(0, w) * max(0, h))
            size = f"{int(w)}x{int(h)}"
            level = "large" if area > 5000 else "small"

            det = {
                "x": int(x1),
                "y": int(y1),
                "width": int(w),
                "height": int(h),
                "confidence": round(conf, 4),
                "label": label,
                "area": area,
                "size": size

            }
            detections.append(det)

            # Nếu có GPS thì lưu
            if gps:
                # get_or_create_pothole(request, user, lat, lon, confidence, size, area)
                try:
                    get_or_create_pothole(request, request.user, gps[0], gps[1], conf, f"{int(w)}x{int(h)}", area, level)
                except Exception as e:
                    # Không block trả response nếu lưu DB lỗi — chỉ log
                    import logging
                    logging.exception("Lỗi khi lưu Pothole: %s", e)

        response = {
            "detections": detections,
            "pothole_count": len(detections),
            "timestamp": timezone.now().isoformat()
        }
        return JsonResponse(response)

    except Exception as e:
        import traceback, logging
        logging.exception("live_detection error: %s", e)
        return JsonResponse({"error": str(e)}, status=500)


def draw_boxes(request, frame, results, user=None, gps=None):
    results = results[0]
    for box in results.boxes:
        # Toạ độ khung ảnh
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = f"{results.names[cls]} {conf:.2f}"

        # Điều chỉnh độ dày viền và font chữ
        line_thickness = 1      # Độ dày viền box
        font_scale = 0.20   # Giảm cỡ chữ từ 0.4 xuống 0.35
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_thickness = 1      # Độ dày của chữ
        
        # Tính toán kích thước text để vẽ nền
        (text_width, text_height), baseline = cv2.getTextSize(
            label, 
            font, 
            font_scale, 
            text_thickness
        )
        
        # Vẽ nền đen cho text để tăng độ tương phản
        cv2.rectangle(frame, 
                     (x1, y1 - text_height - baseline - 2),
                     (x1 + text_width, y1),
                     (0, 0, 0),
                     -1)  # -1 để fill màu
        
        # Vẽ viền box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 100, 0), line_thickness)
        
        # Vẽ text với anti-aliasing
        cv2.putText(frame, 
                   label,
                   (x1, y1 - 2),
                   font,
                   font_scale,
                   (255, 255, 255),     # Màu chữ trắng
                   text_thickness,       # Độ dày chữ
                   cv2.LINE_AA)         # Anti-aliasing để làm mịn chữ

        # Tính area (diện tích bbox)
        area = (x2 - x1) * (y2 - y1)
        size = "large" if area > 5000 else "small"

    return frame

# ================== IMAGE DETECTION ==================
@csrf_exempt
def detect_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        img = cv2.imdecode(np.frombuffer(request.FILES["image"].read(), np.uint8), cv2.IMREAD_COLOR)
        results = model(img, imgsz=960, conf=0.25)

        gps = request.POST.get("gps")
        gps = tuple(map(float, gps.split(","))) if gps else None

        img = draw_boxes(request, img, results, user=request.user, gps=gps)

        _, buffer = cv2.imencode(".jpg", img)
        return JsonResponse({"image": buffer.tobytes().hex()})
    return JsonResponse({"error": "No image uploaded"})


# Cấu hình Roboflow
ROBOFLOW_API_KEY = "rf_d8yBoanGX6bkEsX9Ex8ITPJwhcn2"
ROBOFLOW_WORKSPACE = "vilan-qvsdh"
ROBOFLOW_PROJECT = "pothole-detection-qaqag"
ROBOFLOW_VERSION = 1

def model_training(request):
    code_snippet = None
    uploaded_files = []

    if request.method == "POST" and request.FILES.getlist("images"):
        files = request.FILES.getlist("images")
        save_path = os.path.join(settings.MEDIA_ROOT, "dataset")
        os.makedirs(save_path, exist_ok=True)

        for f in files:
            file_path = os.path.join(save_path, f.name)
            with open(file_path, "wb+") as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            uploaded_files.append(f.name)

        # Tạo đoạn code Colab sẵn sàng
        code_snippet = f"""!pip install roboflow
                            from roboflow import Roboflow
                            rf = Roboflow(api_key="{ROBOFLOW_API_KEY}")
                            project = rf.workspace("{ROBOFLOW_WORKSPACE}").project("{ROBOFLOW_PROJECT}")
                            dataset = project.version({ROBOFLOW_VERSION}).download("yolov11")
                            """

    return render(request, "my_app/model_training.html", {
        "uploaded_files": uploaded_files,
        "code_snippet": code_snippet
    })

