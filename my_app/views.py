from django.shortcuts import render


def dashboard(request):
    return render(request, 'my_app/index.html')

def live_detection(request):
    return render(request, 'my_app/live_detection.html')

def sign_up_and_sign_in(request):
    return render(request, 'my_app/sign_up_and_sign_in.html')

def map(request):
    return render(request, 'my_app/map.html')

def history(request):
    return render(request, 'my_app/history.html')

def account_management(request):
    return render(request, 'my_app/admin/account.html')

def model_training(request):
    return render(request, 'my_app/admin/model_trainning.html')



