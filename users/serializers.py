from rest_framework import serializers
from .models import Otp
from django.contrib.auth import get_user_model
User = get_user_model()
class UserSerializer (serializers.ModelSerializer) :
        class Meta:
            model = User
            exclude = ('password','is_superuser','groups','user_permissions','last_login')

class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ['code']  # only code exists for output
    def create(self, validated_data):
        return Otp.objects.create(**validated_data)