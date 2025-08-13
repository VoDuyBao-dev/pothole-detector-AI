from django.shortcuts import render

# Create your views here.

# my_app/views.py
import os
from django.http import JsonResponse, HttpResponseBadRequest, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pathlib import Path

from .apps import AppConfig  # nếu cần
from inference.detector import detect_image

@csrf_exempt
def detect_upload(request):
    if request.method != "POST" or "image" not in request.FILES:
        return HttpResponseBadRequest("Use POST with form-data and field 'image'.")

    img = request.FILES["image"]
    media_dir = Path(settings.MEDIA_ROOT) / "uploads"
    media_dir.mkdir(parents=True, exist_ok=True)

    # Lưu ảnh tạm
    in_path = media_dir / img.name
    with open(in_path, "wb") as f:
        for chunk in img.chunks():
            f.write(chunk)

    # Chạy detect
    boxes, vis_path = detect_image(str(in_path), save_vis=True)

    # Trả JSON + link ảnh đã vẽ bbox
    rel_vis = None
    if vis_path:
        rel_vis = str(Path(vis_path).relative_to(Path(settings.MEDIA_ROOT)))

    return JsonResponse({
        "count": len(boxes),
        "boxes": boxes,
        "visualization": f"{settings.MEDIA_URL}{rel_vis}" if rel_vis else None
    })
