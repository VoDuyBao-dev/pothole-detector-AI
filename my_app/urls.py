
from django.urls import path

from . import views
from .views import *



urlpatterns = [
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    
    # users
    path('', views.dashboard_view, name= 'dashboard'),

    path("live_detection/", views.live_detection, name="live_detection"),      
    
    path("detect_image/", views.detect_image, name="detect_image"),

    path('map/', views.map, name='map'),
    path('history/', views.history, name='history'),
    path('pothole_detail/<int:pothole_id>/', views.pothole_detail, name='pothole_detail'),


    # admin
    # path('account_management/', views.account_management, name='account_management'),
    # Thêm tài khoản của admin
    path('register/', register_view, name='register'),
    # quản lý tài khoản của admin
    path('accounts/', views.account_list, name='account_list'),
    # sửa tài khoản của admin
    path('edit_account/', views.edit_account, name='edit_account'),
    # xóa tài khoản:
    path('delete_account/', views.delete_account, name='delete_account'),
    #Map hiện ổ gà
    path("api/potholes/", views.pothole_data, name="pothole_data"),
]