from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.viewsets import GenericViewSet
from djoser.views import UserViewSet
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin


User = get_user_model()


# class MyUserViewSet(UserViewSet):
#     def res



class AvatarViewSet(UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = User.objects.all()
