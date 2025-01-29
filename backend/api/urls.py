from django.urls import path, include
from rest_framework import routers
from .views import AvatarViewSet


app_name = 'foodgram_api'
router = routers.DefaultRouter()
router.register(r'avatar', AvatarViewSet)

urlpatterns = [
    path('avatar/', include(router.urls)),
]
