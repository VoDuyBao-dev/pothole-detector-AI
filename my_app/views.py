from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
import cv2, base64, json, os
# import torch
# from ultralytics import YOLO
from openvino.runtime import Core
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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout 
from django.core.paginator import Paginator

import logging
logger = logging.getLogger('my_app')

@login_required
@user_passes_test(lambda u: u.is_superuser)
# Đăng ký tài khoản mới cho user
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        # logger.debug(f"Registering user with email: {email}")
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Email không hợp lệ.')
            return redirect('account_list')

        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại.')
            return redirect('account_list')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
# tạo 1 đối tượng tương ứng bên UserProfile với role mặc định là 'user'
        UserProfile.objects.create(user=user, role='user')

        messages.success(request, 'Tài khoản đã được tạo thành công.')
        return redirect('account_list')
    return redirect('account_list')

@login_required

def dashboard(request):
    return render(request, 'my_app/index.html')


def live_detection(request):
    return render(request, 'my_app/live_detection.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email không hợp lệ.'})

        user = User.objects.filter(email=email).first()

        if user is not None:
            if user.profile.is_deleted:
                return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Tài khoản đã bị xóa.'})
            if user.check_password(password):
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
        return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email hoặc mật khẩu không đúng.'})
    return render(request, 'my_app/sign_up_and_sign_in.html')

@login_required
def signout(request):
    logout(request)
    return redirect('signin')

@login_required
@user_passes_test(lambda u: u.is_superuser)
# danh sách các tài khoản
def account_list(request):
    users = User.objects.filter(is_superuser=False, profile__is_deleted = False)
    return render(request, 'my_app/admin/account.html', {'users':users})

# sửa tài khoản user
@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_account(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(id=user_id)
            # Kiểm tra xem username đã tồn tại chưa (trừ user hiện tại)
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                messages.error(request, 'Tên người dùng đã tồn tại!')
                return redirect('account_list')
            # Kiểm tra xem email đã tồn tại chưa (trừ user hiện tại)
            if User.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, 'Email đã tồn tại!')
                return redirect('account_list')
            
            user.username = username
            user.email = email
            user.save()
            messages.success(request, 'Cập nhật tài khoản thành công!')
        except User.DoesNotExist:
            messages.error(request, 'Tài khoản không tồn tại!')
        
        return redirect('account_list')
    
    return redirect('account_list')

#  xóa tài khoản user (xóa mềm)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_account(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        try:
            user = User.objects.get(id=user_id)
            user.profile.soft_delete()
            messages.success(request, 'Tài khoản đã được xóa mềm thành công!')
        except User.DoesNotExist:
            messages.error(request, 'Tài khoản không tồn tại!')
        return redirect('account_list')
    return redirect('account_list')


def map(request):
    return render(request, 'my_app/map.html')


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
    page_number = request.GET.get("page")
    if _is_admin(request.user):
        potholes = (
            Pothole.objects
            .select_related("first_detected_by")
            .order_by("id")  # Sắp xếp tăng dần theo id
        )
        paginator = Paginator(potholes, 8)
        potholes = paginator.get_page(page_number)

        # Xử lý confidence_avg cho từng item trong trang hiện tại
        for p in potholes:
            p.confidence_avg = p.confidence_avg * 100 if p.confidence_avg else 0

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
        paginator = Paginator(detections, 8)
        detections = paginator.get_page(page_number)

        for d in detections:
            d.pothole.confidence_avg = d.pothole.confidence_avg * 100 if d.pothole.confidence_avg else 0
        return render(request, "my_app/history.html", {
            "is_admin": False,
            "potholes": detections        # template đang dùng biến 'potholes'
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




# # Define model path relative to project root
# MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'pothole_best.pt')

# # Ensure model directory exists
# os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# try:
#     model = YOLO(MODEL_PATH)
# except FileNotFoundError:
#     raise FileNotFoundError(
#         f"Model file not found at {MODEL_PATH}. "
#         "Please ensure the model file 'pothole_best.pt' is placed in the 'models' directory"
#     )



# Load OpenVINO model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'pothole_best_openvino_model/pothole_best.xml')
ie = Core()
model_ov = ie.read_model(MODEL_PATH)
compiled_model = ie.compile_model(model=model_ov, device_name="CPU")

# Lấy input/output tensor
input_layer = compiled_model.input(0)
output_layer = compiled_model.output(0)



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


def live_detection(request):
    return render(request, "my_app/live_detection.html")



def draw_boxes(frame, results, conf_thres=0.25):
    preds = results.T  # (8400, 5)

    h, w = frame.shape[:2]

    for det in preds:
        cx, cy, bw, bh, conf = det
        conf = float(conf)   # ép về float
        if conf < conf_thres:
            continue

        # Chuyển từ center_x,center_y,width,height -> toạ độ góc
        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)
        x2 = int(cx + bw / 2)
        y2 = int(cy + bh / 2)

        # Scale theo kích thước ảnh gốc (nếu resize 640x640 trước khi input)
        scale_x = w / 640
        scale_y = h / 640
        x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
        y1, y2 = int(y1 * scale_y), int(y2 * scale_y)

        # Vẽ box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 100, 0), 1)

        # Chuẩn bị label
        label = f"conf {conf:.2f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.3
        font_thickness = 1

        # Tính kích thước text
        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
        
        # Tính toán vị trí text và background
        text_x = x1
        text_y = max(y1 - 4, text_h + 4)  # Đảm bảo text không bị cắt
        
        # Vẽ background đen cho text
        cv2.rectangle(frame, 
                     (text_x, text_y - text_h - baseline), 
                     (text_x + text_w, text_y + baseline), 
                     (0, 0, 0), 
                     -1)  # -1 để fill đầy

        # Vẽ text
        cv2.putText(frame, 
                   label, 
                   (text_x, text_y),
                   font, 
                   font_scale,
                   (255, 255, 255),  # Màu xanh lá
                   font_thickness,
                   cv2.LINE_AA)

    return frame

# ================== IMAGE DETECTION ==================
@csrf_exempt
def detect_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        logger.debug("hello")
        img = cv2.imdecode(np.frombuffer(request.FILES["image"].read(), np.uint8), cv2.IMREAD_COLOR)
        resized = cv2.resize(img, (640, 640))
        input_image = resized[:, :, ::-1].transpose(2, 0, 1)  # HWC->CHW, BGR->RGB
        input_image = np.expand_dims(input_image, 0).astype(np.float32) / 255.0

        # 3) Inference
        results = compiled_model([input_image])[output_layer]
        # for r in results:
        #     logger.debug(f"Result array: {r}, shape: {r.shape}")  # In ra toàn bộ mảng và shape
        img = draw_boxes(img, results, conf_thres=0.25)

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

