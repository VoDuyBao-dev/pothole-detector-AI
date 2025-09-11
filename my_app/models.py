from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Chứa thông tin tài khoản của người dùng có kế thừa từ AbstractUser để sử dụng các thuộc tính như tên, mật khẩu 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    # xóa mềm
    def soft_delete(self):
        
        self.is_deleted = True
        self.save()

# khôi phục tài khoản
    def restore(self):
    
        self.is_deleted = False
        self.save()

# lưu thông tin ổ gà đầu tiên được phát hiện và các thông tin chung
class Pothole(models.Model):
    STATUS_CHOICES = [
        ('active', 'Chưa sửa'),
        ('fixed', 'Đã sửa'),
    ]

    first_detected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')  # trạng thái ổ gà đã được sửa hay chưa
    confidence_avg = models.FloatField(default=0)   # trung bình độ tin cậy từ các phát hiện
    detections_count = models.PositiveIntegerField(default=1)  # tổng số lần phát hiện

    def __str__(self):
        return f"Ổ gà {self.id} - {self.status}"
# lưu hình ảnh của ổ gà phát hiện được ổ gà trùng cũng được chụp ảnh và lưu
class PotholeImage(models.Model):
    image = models.ImageField(upload_to="potholes/")   # Django sẽ lưu path, file nằm trong MEDIA_ROOT
    uploaded_at = models.DateTimeField(default=timezone.now)

# Lưu thông tin của tất cả ổ gà dù có là ổ gà trùng hay là người đầu tiên phát hiện ra ổ gà thì đều được lưu ở đây
class PotholeDetection(models.Model):
    """Lưu tất cả các lần phát hiện ổ gà (bao gồm cả người đầu tiên)"""
    pothole = models.ForeignKey(Pothole, on_delete=models.CASCADE, related_name="detections")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    size = models.CharField(max_length=20)          # chiều dài x chiều rộng của ổ gà 
    level = models.CharField(max_length=10, choices=[('small', 'Nhỏ'), ('medium', 'Trung bình'), ('large', 'Lớn')])
    confidence = models.FloatField()
    area = models.FloatField(null=True, blank=True)       # diện tích của ổ gà 
    detected_at = models.DateTimeField(default=timezone.now)
    potholeImage_id = models.ForeignKey(PotholeImage, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Detection by {self.user} at {self.detected_at}"


# 5. Bảng ảnh huấn luyện mô hình
class TrainingImage(models.Model):
    image = models.ImageField(upload_to='training_images/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.CharField(max_length=20, choices=[
        ('pothole', 'Pothole'),
        ('no_pothole', 'No Pothole')
    ], default='no_pothole')
    used_in_training = models.BooleanField(default=False) # -> Đánh dấu ảnh này đã được dùng để huấn luyện hay chưa.

    def __str__(self):
        return f"Ảnh huấn luyện {self.id} - {self.uploaded_at}"






