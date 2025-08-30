
from django.urls import path

from . import views
from .views import *



urlpatterns = [
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    
    # users
    path('', views.dashboard, name= 'dashboard'),
    
    path('live_detection/', views.live_detection, name='live_detection'),
    path('map/', views.map, name='map'),
    path('history/', views.history, name='history'),

    # admin
    # path('account_management/', views.account_management, name='account_management'),
    path('model_training/', views.model_training, name='model_training'),
    # Thêm tài khoản của admin
    path('register/', register_view, name='register'),
    # quản lý tài khoản của admin
    path('accounts/', views.account_list, name='account_list'),
    # sửa tài khoản của admin
    path('edit_account/', views.edit_account, name='edit_account'),
    # xóa tài khoản:
    path('delete_account/', views.delete_account, name='delete_account'),
    


]