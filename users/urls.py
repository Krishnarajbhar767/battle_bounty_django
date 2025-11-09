
from rest_framework import routers
from django.urls import path,include
from .views import AuthViewSet,UserViewSet

router = routers.DefaultRouter()
router.register(r'account', UserViewSet,basename='account')
router.register(r'auth', AuthViewSet,basename='auth')

# urlpatterns = [
#     path('',include(router.urls))
# ]

urlpatterns = router.urls
