
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from utils.helpers import delete_all_user_tokens, generate_otp 
from .models import User,Otp
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from .auth_serializers import RegisterSerializer,VerifyOtpSerializer,ResendOtpSerializer,LoginSerializer
import uuid
import hashlib
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()
from  utils.response import error_response,success_response 
from utils.mailer import send_otp_email
class AuthViewSet (viewsets.ViewSet) :
    
    def list(self, request):
        return Response({
            "endpoints": {
                "register": "POST /api/v1/user/auth/register/",
                "login": "POST /api/v1/user/auth/login/",
                "verifyotp": "POST /api/v1/user/auth/verifyotp/",
                "logout": "POST /api/v1/user/auth/logout/",
                "refresh_token": "POST /api/v1/user/auth/refresh_token/",
                "resend_otp": "POST /api/v1/user/auth/resend_otp/"

            }
        })   
    @action(detail=False, methods=["post"])
    def register(self, request):
        # get request data
        data = request.data 
        # verify data from serializer
        regsiter_serializer = RegisterSerializer(data = data)
        # if given data is valid then go forward
        if  regsiter_serializer.is_valid() : 
            # craete  new user from given data with active=false 
            user = regsiter_serializer.save() 
            # generate new otp
            otp_code = generate_otp(user)
            # once otp successfully created then send to user otp
            send_otp_email(recipient_email=data['email'],user_first_name=data['first_name'],otp_code=otp_code),
            return success_response('Otp Sent Successfully. Please Verify your account.') 
        return  error_response(errors=regsiter_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       
    @action(detail=False,methods=['post'])   
    def verifyotp (self,request) :
        data  = request.data
        serializer = VerifyOtpSerializer(data = data)
        if serializer.is_valid() :
            print('Printing OTP Serializer Validated Data',serializer.validated_data)
            user = serializer.validated_data['user']
            found_otp = serializer.validated_data['found_otp']
            user.is_active = True
            user.save()
            found_otp.delete()
            return success_response('Account verified successfully.',status=status.HTTP_201_CREATED)
        
        return error_response ('Account verification failed',errors=serializer.errors)

    @action(detail=False,methods=['post']) 
    def resend_otp(self,request) :
        data = request.data
        serializer = ResendOtpSerializer(data=data)
        if serializer.is_valid() :
            user = serializer.validated_data["user"]
             # Check existing OTP
            existing_otp = Otp.objects.filter(user=user).order_by("-created_at").first()
            # Stop User For Sending Too Many  Re-Send Request
            if existing_otp and not existing_otp.is_expired() :
                time_diff = (timezone.now() - existing_otp.created_at).seconds
                if time_diff < 60 :  # 60 sec cooldown
                    return error_response(f"Please wait {60 - time_diff} seconds before requesting another OTP", status=status.HTTP_429_TOO_MANY_REQUESTS)
                # generate new otp
                
            otp_code = generate_otp(user)
            send_otp_email(recipient_email=user.email,user_first_name=user.first_name,otp_code=otp_code)
            return success_response('Otp Sent Successfully.',status=status.HTTP_201_CREATED) 
        
        return  error_response(errors=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False,methods=['post'])
    def login (self,request) :
        data = request.data
        serializer = LoginSerializer(data = data)
        if serializer.is_valid() :
            user = serializer.validated_data["user"]
            user_data = UserSerializer(user).data
            
            # Before Creating Token For User  Delete All Thair  Access And Refresh Token
            delete_all_user_tokens(user)
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            # Return Json Data
            response = Response({
                        "success":True,
                        "message": "Login successful",
                        "data": user_data,
                        "access_token": str(access),
                    })
            
            # set refresh token as cookie
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,       # set False only in localhost
                samesite="Lax",
                max_age=7 * 24 * 60 * 60
            )
            return response
        return  error_response(errors=serializer.errors,status=status.HTTP_400_BAD_REQUEST)      
    
    @action(detail=False, methods=["post"])
    def logout(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        try:
            token = RefreshToken(refresh_token)
            user_id = token.payload.get("user_id")
            user = User.objects.get(id=user_id)
            delete_all_user_tokens(user)
           
        except:
            pass

        response =  success_response(message='Logged out everywhere')
        response.delete_cookie("refresh_token")
        return  response  
         
    @action(detail=False, methods=["post"]) 
    def refresh_token(self,request) :
        refresh = request.COOKIES.get("refresh_token")
        if not refresh :
            return error_response('Refresh Token Not Found',status=401)
        try :
            # Generate New Refresh And  Access Token
            user = RefreshToken(refresh).payload.get("user_id")
            # Kill all old tokens
            delete_all_user_tokens(User.objects.get(id=user))
            # get access token
            new_refresh = RefreshToken.for_user(User.objects.get(id=user))
            new_access = new_refresh.access_token
            # send success resposne
            response = success_response(data=str(new_access),message="Tokens Refreshed",status=201)
            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                httponly=True,
                secure=False, #False in DEVELOPEMENT
                samesite="Lax",
                max_age=7 * 24 * 60 * 60
            )
            return response
        except Exception:
            return error_response('Invalid refresh token. Login again.',status=401)

    @action (detail=False,methods=['post'])
    def reset_password (self,request) :
        data = request.data
        serializer = 
        
class UserViewSet (viewsets.ViewSet) :
    def list(self, request):
        return Response({
            "endpoints": {
                "me": "GET /api/v1/user/account/me/",
            }
        })   
    @action(detail=False,methods=['get']) 
    def me(self,request) :
        user = UserSerializer(request.user).data  # important
        return Response({'message':'User Fetch Successfull',"user":user},status=200)

    
        