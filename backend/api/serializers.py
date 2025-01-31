import base64
import os
import uuid
import logging
import pathlib

import django.conf
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from djoser.conf import settings
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, CharField, ModelField, IntegerField, Field
from rest_framework.serializers import ImageField, ModelSerializer, Serializer
from foodgram.models import Subcription

User = get_user_model()
logger = logging.getLogger(__name__)

class AvatarUserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(max_length=255)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        ]


    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if Subcription.objects.filter(user=user, subscribed_to=obj).exists():
            return True
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        # Для текущего пользователя подписка всегда не активна,
        # незачем отправлять запрос в БД
        if request.path == r'/api/users/me/':
            representation['is_subscribed'] = False
        elif request.path == r'/api/users/me/avatar/':
            representation = {'avatar': representation['avatar']}
        return representation


class SubscriptionSerializer(Serializer):
    id = SerializerMethodField()

    class Meta:
        fields = ('id',)

    def get_id(self, obj, request):
        return -1

class AvatarField(Field):
    def to_internal_value(self, data):
        if not data.startswith('data:image/'):
            raise ValidationError("Неверный формат данных изображения.")
        # Извлекаем формат и данные изображения
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]  # Получаем расширение файла

        logger.debug(f'My variable value: {imgstr}')
        # Генерируем уникальное имя для файла
        id = uuid.uuid4()
        file_name = f"{id}.{ext}"
        os.makedirs(django.conf.settings.MEDIA_ROOT / 'avatars', exist_ok=True)
        with open(django.conf.settings.MEDIA_ROOT / 'avatars', "wb") as f:
            f.write(base64.b64decode(imgstr))
        try:
            decoded_file = ContentFile(base64.b64decode(imgstr), name=file_name)
            return f'/media/avatars/{file_name}'
        except Exception as e:
            logger.debug(f'My variable value: {imgstr}')
            return None


    def to_representation(self, value):
        return value



class AvatarSerializer(ModelSerializer):
    avatar = AvatarField()

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        if 'avatar' in validated_data:
            instance.avatar.save(validated_data['avatar'].name, validated_data['avatar'])

        instance.save()
        return instance


