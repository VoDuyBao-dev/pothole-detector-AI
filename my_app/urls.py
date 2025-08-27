
from django.urls import path

from . import views
from .views import *



urlpatterns = [
    path('', views.dashboard, name= 'dashboard'),
    path('live_detection/', views.live_detection, name='live_detection'),
    path("camera_feed/", views.camera_feed, name="camera_feed"),
    path("video_upload/", views.video_upload, name="video_upload"),
    path("detect_image/", views.detect_image, name="detect_image"),

    path('sign_up_and_sign_in/', views.sign_up_and_sign_in, name='sign_up_and_sign_in'),
    path('map/', views.map, name='map'),
    path('history/', views.history, name='history'),
    path('account_management/', views.account_management, name='account_management'),
    path('model_training/', views.model_training, name='model_training'),

]