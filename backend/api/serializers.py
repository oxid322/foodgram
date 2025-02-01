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
from rest_framework.fields import SerializerMethodField, CharField, Field, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from foodgram.models import Subscription, Ingredient, Recipe, RecipeIngredient

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


#TODO: реализовать сериализатор подписки
class SubscriptionSerializer(Serializer):
    id = SerializerMethodField()

    class Meta:
        fields = ('id',)

    def get_id(self, obj, request):
        return -1


# class AvatarField(Field):
#     """Поле аватара"""
#     def to_internal_value(self, data):
#         if not data.startswith('data:image/'):
#             raise ValidationError("Неверный формат данных изображения.")
#         # Извлекаем формат и данные изображения
#         format, imgstr = data.split(';base64,')
#         ext = format.split('/')[-1]  # Получаем расширение файла
#
#         logger.debug(f'My variable value: {imgstr}')
#         # Генерируем уникальное имя для файла
#         id = uuid.uuid4()
#         file_name = f"{id}.{ext}"
#         os.makedirs(django.conf.settings.MEDIA_ROOT / 'avatars', exist_ok=True)
#         with open(django.conf.settings.MEDIA_ROOT / 'avatars', "wb") as f:
#             f.write(base64.b64decode(imgstr))
#         try:
#             decoded_file = ContentFile(base64.b64decode(imgstr), name=file_name)
#             return f'/media/avatars/{file_name}'
#         except Exception as e:
#             logger.debug(f'My variable value: {imgstr}')
#             return None
#
#     def to_representation(self, value):
#         return value


class AvatarSerializer(ModelSerializer):
    """Сериализатор для аватара"""
    avatar = Base64ImageField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(PasswordSerializer):
    """Кастомный сериализатор смены пароля"""
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


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class RecipeSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_in_shopping_cart = SerializerMethodField()
    is_favorited = SerializerMethodField()
    author = AvatarUserSerializer(read_only=True)
    image = Base64ImageField(max_length=255, required=False)
    cooking_time = IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_cooking_time(self, value):
        if value >= 1:
            return value
        else:
            raise ValidationError('Время готовки должно быть больше либо равно 1')
