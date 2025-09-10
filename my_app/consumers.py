# app/consumers.py
import base64, cv2, numpy as np, json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

class DetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            frame_b64 = data.get("frame")
            gps = data.get("gps")

            if not frame_b64:
                return

            img_bytes = base64.b64decode(frame_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            results = model(frame)  # chạy YOLO/OpenVINO
            res0 = results[0]
            names = getattr(res0, "names", None) or {}
            detections = []

            for box in res0.boxes:
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = names.get(cls, str(cls))
                w, h = x2 - x1, y2 - y1
                area = int(max(0, w) * max(0, h))
                size = f"{w}x{h}"
                level = "large" if area > 5000 else "small"

                detections.append({
                    "x": x1, "y": y1, "width": w, "height": h,
                    "confidence": round(conf, 4), "label": label,
                    "area": area, "size": size, "level": level
                })

            response = {
                "detections": detections,
                "pothole_count": len(detections),
                "timestamp": timezone.now().isoformat()
            }
            await self.send(text_data=json.dumps(response))

        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
