import hashlib
from rest_framework import serializers
from django.contrib.auth import get_user_model 
from django.utils.crypto import get_random_string
from .models import Otp
from django.utils import timezone
import uuid
from datetime import timedelta
from utils.response import error_response,success_response
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
User = get_user_model()

class RegisterSerializer (serializers.ModelSerializer) :
    # This Means Password is required and its only used for write only  not  send password in response
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['first_name','last_name','email', 'password', 'confirm_password']
        
        
    def validate(self, data):
        # Check is both password are same or not ? 
        if data['password'] != data['confirm_password'] :
            raise serializers.ValidationError({"password":"Password do not match"})
        # Lowercase email before saving in db
        email = data.get('email', '').lower()
        data['email'] = email
        # Get User If Exist
        user = User.objects.filter(email=email).first()
        # If User exist and its also active 
        if user and user.is_active :
            raise serializers.ValidationError({"email": "Email already registered"})
    
        return data
       
        
    def create(self, validated_data):
        # get Email From Validated Data
        email = validated_data["email"]
        # Check if user exists but not verified
        user = User.objects.filter(email=email).first()
        if user and not user.is_active :
            return user  
        # Create New User After Validating
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False
        )
        return user

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        # get  data from data that is recieved from serializer defualt
        email = attrs.get("email")
        user_given_otp = attrs.get("otp")
        # get user from matched email data
        user = User.objects.filter(email=email).first()
        # if not user found the throw user not found
        if not user:
            raise serializers.ValidationError({"email": "User not found"})
        # if user found but he is already active 
        if  user.is_active :
            raise serializers.ValidationError({"email": "User is already verified"})
        # if user existed then find is he requested otp or not ? 
        hashed_otp = hashlib.sha256(user_given_otp.encode()).hexdigest()
        db_found_otp = Otp.objects.filter(user=user, otp=hashed_otp).first()
        # if not registration request or otp found then throw Invalid otp user
        if not db_found_otp:
            raise serializers.ValidationError({"otp": "Invalid OTP"})
        # check is otp is valid or not ? 
        if db_found_otp.is_expired():
            # if otp  expired then delete and throw error
            db_found_otp.delete()
            raise serializers.ValidationError({"otp": "OTP expired"})
        # attach user and otp_obj
        attrs["user"] = user
        attrs["found_otp"] = db_found_otp
        return attrs

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        attrs['email'] = email
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email": "User not found"})

        if user.is_active:
            raise serializers.ValidationError({"email": "User already verified"})

        attrs["user"] = user
        return attrs

class LoginSerializer (serializers.Serializer) :
    email = serializers.EmailField() 
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")
        
        user = User.objects.filter(email= email).first()
        # Check Is User Exist or not
        if not user:
            raise AuthenticationFailed("Please sign up first")
        
        # if user exist  and then check is he active or not ? 
        if  user and not user.is_active :
            raise AuthenticationFailed("Account not verified. Please verify OTP first.")
        
        # Now Login User
        user = authenticate(username=email, password=password)
        if not user :
            raise AuthenticationFailed("Invalid credentials")
        
        attrs["user"] = user
        return attrs

class ResetPassword(serializers.Serializer) :
    email = serializers.EmailField()
    
    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email)
        if not user :
            
            
        
        
         