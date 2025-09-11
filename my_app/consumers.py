# app/consumers.py
import base64, cv2, numpy as np, json, math
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.contrib import messages
from .models import Pothole, PotholeDetection
from .ml_model import run_inference  # ✅ gọi hàm từ file ml_model.py
import logging
logger = logging.getLogger('my_app')


# # ================== HIỂN THỊ THÔNG BÁO ==================
# def phatHienOGa(request):
#     messages.success(request, "✅ Thêm ổ gà mới vào CSDL thành công!")

# def gpsWarning(request):
#     messages.error(request, "⚠️ Không có GPS, không thể lưu vị trí ổ gà!")


# ================== HÀM HỖ TRỢ ==================
def haversine(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 toạ độ GPS (mét)"""
    R = 6371000  # bán kính Trái Đất (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return distance


def get_or_create_pothole(user, lat, lon, confidence, size, area, level):
    """
    Kiểm tra xem đã có ổ gà trong phạm vi threshold chưa.
    Nếu có: cập nhật. Nếu chưa: tạo mới.
    Luôn lưu vào PotholeDetection.
    """

    threshold = 1 # mét, bán kính gom cụm
    nearby = None

    # 🔹 Lọc trước theo bounding box nhỏ để tăng hiệu năng
    delta = 0.0001  # ~11m
    candidates = Pothole.objects.filter(
        latitude__range=(lat - delta, lat + delta),
        longitude__range=(lon - delta, lon + delta)
    )

    for pothole in candidates:
        if haversine(lat, lon, pothole.latitude, pothole.longitude) < threshold:
            nearby = pothole
            break

    if nearby:
        # Cập nhật confidence trung bình
        old_count = nearby.detections_count
        nearby.detections_count += 1
        nearby.confidence_avg = (nearby.confidence_avg * old_count + confidence) / nearby.detections_count
        nearby.save()
    else:
        # Tạo ổ gà mới
        nearby = Pothole.objects.create(
            first_detected_by=user,
            confidence_avg=confidence,
            detections_count=1,
            status='active'
        )

    # Luôn lưu detection mới
    PotholeDetection.objects.create(
        pothole=nearby,
        user=user,
        latitude=lat,
        longitude=lon,
        size=size,
        confidence=confidence,
        area=area,
        level=level,
        detected_at=timezone.now(),
        potholeImage_id=None
    )

    return nearby


# ================== WEBSOCKET CONSUMER ==================
# AsyncWebsocketConsumer: class Django Channels để giao tiếp WebSocket.
class DetectionConsumer(AsyncWebsocketConsumer):   
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            frame_b64 = data.get("frame")
            gps = data.get("gps")
            user = self.scope["user"] if self.scope["user"].is_authenticated else None
            logger.debug(f"User: {user}, GPS: {gps}")

            if not frame_b64:
                logger.warning("Không có frame → không xử lý gì cả")
                return

            # Giải mã frame thành ảnh OpenCV
            img_bytes = base64.b64decode(frame_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            
            # ✅ Gọi model từ ml_model.py
            detections = run_inference(frame)
            pothole_count = len(detections) or 0 

            if not detections:
                logger.debug(f"Không phát hiện ổ gà trong frame → không gửi dữ liệu về client: {pothole_count}")
                return
            
            # Nếu có GPS -> kiểm tra ổ gà & lưu
            if gps and "lat" in gps and "lon" in gps:
                lat, lon = float(gps["lat"]), float(gps["lon"])
                for det in detections:
                    get_or_create_pothole(
                        user=user,
                        lat=lat,
                        lon=lon,
                        confidence=det["confidence"],
                        size=det["size"],
                        area=det["area"],
                        level=det["level"]
                    )
            else:
                logger.warning("Không có GPS → chỉ trả về kết quả detection")

            # Trả kết quả về client
            response = {
                "detections": detections,
                "pothole_count": pothole_count,
                "confidence_TB": round(float(detections[pothole_count-1]["confidence_TB"]), 4) if detections else 0,
                "timestamp": timezone.now().isoformat()
            }
            await self.send(text_data=json.dumps(response))

        except Exception as e:
            logger.error(f"Lỗi trong DetectionConsumer: {str(e)}")
            await self.send(text_data=json.dumps({"error": str(e)}))
