from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import action

from .serializers import AvatarUserSerializer
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from djoser.views import UserViewSet
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

User = get_user_model()


class MyUserViewSet(ModelViewSet):

    serializer_class = AvatarUserSerializer
    queryset = User.objects.all()

    def get_instance(self):
        return self.request.user

    @action(['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


class AvatarViewSet(UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = User.objects.all()
