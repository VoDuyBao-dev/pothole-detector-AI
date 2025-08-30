from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout  
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_superuser)
# Đăng ký tài khoản mới cho user
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Email không hợp lệ.')
            return redirect('account_list')

        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email đã tồn tại.')
            return redirect('account_list')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
# tạo 1 đối tượng tương ứng bên UserProfile với role mặc định là 'user'
        UserProfile.objects.create(user=user, role='user')

        messages.success(request, 'Tài khoản đã được tạo thành công.')
        return redirect('account_list')
    return redirect('account_list')

@login_required

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

        if user is not None:
            if user.profile.is_deleted:
                return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Tài khoản đã bị xóa.'})
            if user.check_password(password):
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
        return render(request, 'my_app/sign_up_and_sign_in.html', {'error': 'Email hoặc mật khẩu không đúng.'})
    return render(request, 'my_app/sign_up_and_sign_in.html')

@login_required
def signout(request):
    logout(request)
    return redirect('signin')


def map(request):
    return render(request, 'my_app/map.html')

def history(request):
    return render(request, 'my_app/history.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
# danh sách các tài khoản
def account_list(request):
    users = User.objects.filter(is_superuser=False, profile__is_deleted = False)
    return render(request, 'my_app/admin/account.html', {'users':users})

# sửa tài khoản user
@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_account(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(id=user_id)
            # Kiểm tra xem username đã tồn tại chưa (trừ user hiện tại)
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                messages.error(request, 'Tên người dùng đã tồn tại!')
                return redirect('account_list')
            # Kiểm tra xem email đã tồn tại chưa (trừ user hiện tại)
            if User.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, 'Email đã tồn tại!')
                return redirect('account_list')
            
            user.username = username
            user.email = email
            user.save()
            messages.success(request, 'Cập nhật tài khoản thành công!')
        except User.DoesNotExist:
            messages.error(request, 'Tài khoản không tồn tại!')
        
        return redirect('account_list')
    
    return redirect('account_list')

#  xóa tài khoản user (xóa mềm)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_account(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        try:
            user = User.objects.get(id=user_id)
            user.profile.soft_delete()
            messages.success(request, 'Tài khoản đã được xóa mềm thành công!')
        except User.DoesNotExist:
            messages.error(request, 'Tài khoản không tồn tại!')
        return redirect('account_list')
    return redirect('account_list')


def model_training(request):
    return render(request, 'my_app/admin/model_trainning.html')



