from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from .manager import UserManager
from django.utils import timezone
import hashlib


class User (AbstractUser) :
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True)
    avatar = models.URLField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    dob = models.DateField(blank=True,null=True)
    google_id = models.CharField(max_length=255, blank=True)
    # Is is Staff  False Then Thats  Means its an User
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def __str__(self):
         return self.username
    
    
class Address (models.Model) :
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='address')
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    def __str__(self):
            return f"{self.user.email}"
        
 
class Kyc (models.Model) :
        user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kyc'
     )
        aadhaar =   models.CharField(max_length=16)
        pancard = models.CharField(max_length=10)
        aadharFrontImage = models.CharField()
        aadharBackImage = models.CharField()
        pancardImage = models.CharField()
        isVerified = models.BooleanField(default=False)
        def __str__(self):
            return f"{self.user.email}"
        
class Otp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Function For Check Is Current OTP Is Valid Or Not
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
    
    # Check MATCH OTP Function 
    def check_otp (self,otp) :
        hashed = hashlib.sha256(otp.encode()).hexdigest()
        return self.otp == hashed
    
    
    def __str__(self):
     return self.user.email