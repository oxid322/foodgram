import base64

from django.core.files.base import ContentFile
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from djoser.views import UserViewSet
from rest_framework.mixins import (UpdateModelMixin,
                                   DestroyModelMixin,
                                   CreateModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from foodgram.models import Subcription
from .serializers import AvatarUserSerializer, SubscriptionSerializer, AvatarSerializer
from .pagination import CustomPagination

User = get_user_model()


class MyUserViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = AvatarUserSerializer
    queryset = User.objects.all()


    def get_instance(self):
        return self.request.user

    @action(['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


class SubscriptionViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subcription.objects.all()
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        # if serializer.is_valid(raise_exception=False):
        sub_to = None
        try:
            sub_to = User.objects.get(id=self.kwargs['id'])
            Subcription.objects.get(user=user, subscribed_to=sub_to)
            return Response({'detail': 'Подписка уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            if not sub_to:
                return Response({'detail': 'Пользователя не существует'},
                                status=status.HTTP_404_NOT_FOUND)
            if user == sub_to:
                return Response({'detail': 'Нельзя подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            sub = Subcription.objects.create(user=user, subscribed_to=sub_to)
            return Response({'id': self.kwargs['id']}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']
        user = self.request.user
        try:
            sub_to = User.objects.get(id=id)
            try:
                sub = Subcription.objects.get(user=user, subscribed_to=sub_to)
                sub.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response({'detail': 'Вы не подписаны на пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'detail': 'Пользователя не существует'}, status=status.HTTP_404_NOT_FOUND)
    #TO DO: def list





class AvatarViewSet(UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AvatarUserSerializer
    permission_classes = (IsAuthenticated,)



    def update(self, request, *args, **kwargs):
        instance = self.get_queryset().get(id=self.request.user.id)
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
