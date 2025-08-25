
from django.urls import path

from . import views
from .views import *



urlpatterns = [
    path('', views.dashboard, name= 'dashboard'),
    path('hard/', views.hard_dashboard, name= 'hard_dashboard'),
    path('live_detection/', views.live_detection, name='live_detection'),
    path('sign_up_and_sign_in/', views.sign_up_and_sign_in, name='sign_up_and_sign_in'),
    path('map/', views.map, name='map'),
    path('history/', views.history, name='history'),
    path('account_management/', views.account_management, name='account_management'),
    path('model_training/', views.model_training, name='model_training'),

]