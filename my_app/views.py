from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout  

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'my_app/admin/account.html', {'error': 'Email không hợp lệ.'})

        
        if User.objects.filter(username=email).exists():
            return render(request, 'my_app/admin/account.html', {'error': 'Email đã tồn tại.'})
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
# tạo 1 đối tượng tương ứng bên UserProfile với role mặc định là 'user'
        UserProfile.objects.create(user=user, role='user')

        return render(request, 'my_app/admin/account.html', {'success': 'Tài khoản đã được tạo thành công.'})
    return redirect('account_management')



def dashboard(request):
    return render(request, 'my_app/index.html')

def live_detection(request):
    return render(request, 'my_app/live_detection.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email không hợp lệ.'})

        user = User.objects.filter(username=email).first()

        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email hoặc mật khẩu không đúng.'})
        
    return render(request, 'my_app/sign_up_and_sign_in.html')

def signout(request):
    logout(request)
    return redirect('signin')

def map(request):
    return render(request, 'my_app/map.html')

def history(request):
    return render(request, 'my_app/history.html')

def account_management(request):
    return render(request, 'my_app/admin/account.html')

def model_training(request):
    return render(request, 'my_app/admin/model_trainning.html')



