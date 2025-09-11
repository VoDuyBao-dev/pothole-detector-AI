from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
import cv2, os, base64
import numpy as np
from django.http import  JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import * 
from .ml_model import run_inference, draw_boxes
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout  
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
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




def live_detection(request):
    return render(request, "my_app/live_detection.html")


# ================== IMAGE DETECTION ==================
@csrf_exempt
def detect_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        # Đọc ảnh từ request
        img = cv2.imdecode(
            np.frombuffer(request.FILES["image"].read(), np.uint8), 
            cv2.IMREAD_COLOR
        )

        # Gọi inference chung
        detections = run_inference(img)
        pothole_count = len(detections) or 0 
        logger.debug(f"có bao nhiêu ổ gà trong ảnh: {detections}")

        # Vẽ bounding boxes
        img = draw_boxes(img, detections, conf_thres=0.25)

        # Encode thành base64
        _, buffer = cv2.imencode(".jpg", img)
        img_base64 = base64.b64encode(buffer).decode("utf-8")

        safe_detections = []
        for d in detections:
            safe_detections.append({
                "x": int(d.get("x", 0)),
                "y": int(d.get("y", 0)),
                "width": int(d.get("width", 0)),
                "height": int(d.get("height", 0)),
                "confidence": float(d.get("confidence", 0)),
                "label": d.get("label", ""),
                "area": int(d.get("area", 0)),
                "size": d.get("size", ""),
                "level": d.get("level", "")
            })

        return JsonResponse({
            "image": img_base64,
            "detections": safe_detections,
            "confidence_TB": round(float(detections[pothole_count-1]["confidence_TB"]), 4) if detections else 0
        })

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

