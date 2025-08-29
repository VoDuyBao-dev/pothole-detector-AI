
from django.urls import path

from . import views
from .views import *



urlpatterns = [
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    
    # users
    path('', views.dashboard, name= 'dashboard'),

    path("live_detection_page/", views.live_detection_page, name="live_detection_page"),  # trả template
    path("live_detection/", views.live_detection, name="live_detection"),        # POST nhận frame
    
    path("detect_image/", views.detect_image, name="detect_image"),

    path('map/', views.map, name='map'),
    path('history/', views.history, name='history'),

    # admin
    path('account_management/', views.account_management, name='account_management'),
    path('model_training/', views.model_training, name='model_training'),
    # Thêm tài khoản của admin
    path('register/', views.register_view, name='register'),
    


]