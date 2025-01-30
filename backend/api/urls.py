from django.urls import path, include
from rest_framework import routers
from .views import AvatarViewSet, MyUserViewSet


app_name = 'foodgram_api'
router = routers.DefaultRouter()
router.register(r'', MyUserViewSet)
# router.register(r'/me/avatar', AvatarViewSet, basename='avatar')

urlpatterns = router.urls