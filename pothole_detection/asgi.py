"""
ASGI config for pothole_detection project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pothole_detection.settings')

# application = get_asgi_application()



# project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from app.consumers import WebRTCConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')


django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
"http": django_asgi_app,
"websocket": AuthMiddlewareStack(
URLRouter([
path("ws/signalling/", WebRTCConsumer.as_asgi()),
])
),
})