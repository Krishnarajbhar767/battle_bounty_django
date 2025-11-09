# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager 
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
import uuid
class UserManager(BaseUserManager):

    # These are the new instructions for creating users.
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        # Lowercase and clean the email for uniqueness
        email = self.normalize_email(email).lower()
        # craete Default Username  From user email
        username = email.split('@')[0]
        if self.model.objects.filter(username=username).exists():
            username = f"{username}_{str(uuid.uuid4())[:8]}"

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)