import base64
import logging
import os
import uuid

import django.conf
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, PasswordSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, CharField, Field
from rest_framework.serializers import ModelSerializer, Serializer

from foodgram.models import Subscription

User = get_user_model()
logger = logging.getLogger(__name__)


class AvatarUserSerializer(UserCreateSerializer):
    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(max_length=255, required=False)

    class Meta:
        model = User
        fields = (
                     tuple(User.REQUIRED_FIELDS)) + (
                     'email',
                     'id',
                     'is_subscribed',
                     'avatar',
                 )
        read_only_fields = ['is_subscribed', 'id', 'email']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            if Subscription.objects.filter(user=user, subscribed_to=obj).exists():
                return True
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        # Для текущего пользователя подписка всегда не активна,
        # незачем отправлять запрос в БД
        if request.path == r'/api/users/me/' or not request.user.is_authenticated:
            representation['is_subscribed'] = False
        elif request.path == r'/api/users/me/avatar/':
            representation = {'avatar': representation['avatar']}
        return representation

    # def create(self, validated_data):
    #     user = User()


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
    avatar = Base64ImageField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(PasswordSerializer):
    current_password = CharField(write_only=True, required=True)

    class Meta:
        fields = ('current_password', 'new_password')

    def get_user(self):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return user
        return None

    def validate_current_password(self, password):
        user = self.context['request'].user
        if user.check_password(password):
            return password
        raise ValidationError('Пароль неверен')
