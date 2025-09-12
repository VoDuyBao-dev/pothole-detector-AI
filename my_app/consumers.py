# app/consumers.py
import base64, cv2, numpy as np, json, math
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
import asyncio
from django.core.files.base import ContentFile
from .models import Pothole, PotholeDetection, PotholeImage
from .ml_model import run_inference, draw_boxes
import logging

logger = logging.getLogger('my_app')


# ================== HÀM HỖ TRỢ ==================
def haversine(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 toạ độ GPS (mét)"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@database_sync_to_async
def get_or_create_pothole(user, lat, lon, det, pothole_image):
    """
    Kiểm tra ổ gà đã tồn tại chưa.
    Nếu có: cập nhật lại confidence_avg + detections_count.
    Nếu chưa: tạo mới.
    Sau đó lưu PotholeDetection (liên kết với ảnh frame).
    """
    confidence = det["confidence"]
    size = det["size"]
    area = det["area"]
    level = det["level"]

    threshold = 1  # mét
    nearby = None

    # Lọc những pothole có detection gần đó
    delta = 0.00005  # khhoảng ~5,5m
    candidates = Pothole.objects.filter(
        detections__latitude__range=(lat - delta, lat + delta),
        detections__longitude__range=(lon - delta, lon + delta)
    ).distinct()

    for pothole in candidates:
        # lấy detection gần nhất (mới nhất) của ổ gà này
        last_detection = pothole.detections.order_by("-detected_at").first()
        if last_detection and haversine(lat, lon, last_detection.latitude, last_detection.longitude) < threshold:
            nearby = pothole
            break

    if nearby:
        # Cập nhật confidence trung bình
        old_count = nearby.detections_count
        nearby.detections_count += 1
        nearby.confidence_avg = (nearby.confidence_avg * old_count + confidence) / nearby.detections_count
        nearby.save()
    else:
        nearby = Pothole.objects.create(
            first_detected_by=user,
            confidence_avg=confidence,
            detections_count=1,
            status="active",
        )

    # Tạo bản ghi detection
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
        potholeImage_id=pothole_image
    )

    return nearby


@database_sync_to_async
def save_pothole_image(frame):
    """Lưu frame có bounding box thành 1 bản ghi PotholeImage"""
    _, buffer = cv2.imencode(".jpg", frame)
    image_file = ContentFile(buffer.tobytes(), name=f"pothole_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    pothole_image = PotholeImage.objects.create(image=image_file)
    return pothole_image


# ================== WEBSOCKET CONSUMER ==================
class DetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            frame_b64 = data.get("frame")
            gps = data.get("gps")
            user = self.scope["user"] if self.scope["user"].is_authenticated else None

            if not frame_b64:
                logger.warning("❌ Không có frame gửi lên → bỏ qua")
                return

            # Giải mã frame
            img_bytes = base64.b64decode(frame_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # YOLO detect
            detections = await asyncio.to_thread(run_inference, frame)
            pothole_count = len(detections)

            # Vẽ 1 frame duy nhất với tất cả bounding boxes
            frame_with_boxes = draw_boxes(frame.copy(), detections, conf_thres=0.25)

            pothole_image = None
            if gps and "lat" in gps and "lon" in gps:
                lat, lon = float(gps["lat"]), float(gps["lon"])
                pothole_image = await save_pothole_image(frame_with_boxes)

                # Với mỗi ổ gà → tạo detection + cập nhật Pothole
                for det in detections:
                    await get_or_create_pothole(user, lat, lon, det, pothole_image)
            else:
                logger.warning("⚠️ Không có GPS → chỉ trả về ảnh bounding box")

            # Encode ảnh trả về client
            _, buffer = cv2.imencode(".jpg", frame_with_boxes)
            frame_base64 = base64.b64encode(buffer).decode("utf-8")

            response = {
                "pothole_count": pothole_count,
                "image": frame_base64,
                "timestamp": timezone.now().isoformat(),
                "confidence_TB": round(float(detections[pothole_count-1]["confidence_TB"]), 4) if detections else 0
            }
            await self.send(text_data=json.dumps(response))

        except Exception as e:
            logger.error(f"Lỗi trong DetectionConsumer: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({"error": str(e)}))
