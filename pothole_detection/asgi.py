"""
ASGI config for pothole_detection project.
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pothole_detection.settings')

import django
django.setup()


from django.core.asgi import get_asgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import my_app.routing



# Lấy ứng dụng Django
django_asgi_app = get_asgi_application()

# Nếu đang DEBUG thì bọc thêm StaticFilesHandler
if settings.DEBUG:
    django_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            my_app.routing.websocket_urlpatterns
        )
    ),
})


# uvicorn pothole_detection.asgi:application --reload --port 8000

