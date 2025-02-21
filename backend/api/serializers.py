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

from foodgram.models import Subscription, Ingredient, Recipe, RecipeIngredient, Favorite

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomUserSerializer(UserCreateSerializer):
    """Кастомный сериализатор пользователя"""
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
        # переопределим метод, чтобы нужные вещи выводились
        representation = super().to_representation(instance)
        request = self.context.get('request')
        # Для текущего пользователя подписка всегда не активна,
        # незачем отправлять запрос в БД
        if request.path == '/api/users/me/' or not request.user.is_authenticated:
            representation['is_subscribed'] = False
        elif request.path == '/api/users/me/avatar/':
            representation = {'avatar': representation['avatar']}
        return representation


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
    avatar = Base64ImageField(max_length=255, required=True)

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
    ingredients = IngredientSerializer(many=True,
                                       read_only=True)
    is_favorited = SerializerMethodField()
    #is_in_shopping_cart = SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=255,
                             required=False)
    cooking_time = IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'ingredients',
                  'is_favorited',
                  #'is_in_shoping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',)

    def __init__(self, *args, **kwargs):
        # Убираем поле `author`, если передан параметр `exclude_author=True` и т д
        exclude_author = kwargs.pop('exclude_author', False)
        exclude_ingredients = kwargs.pop('exclude_ingredients',
                                         False)
        exclude_text = kwargs.pop('exclude_text', False)
        exclude_serializer_method = kwargs.pop('exclude_serializer_method', False)

        super().__init__(*args, **kwargs)

        if exclude_author:
            self.fields.pop('author')

        if exclude_ingredients:
            self.fields.pop('ingredients')

        if exclude_text:
            self.fields.pop('text')

        if exclude_serializer_method:
            self.fields.pop('is_favorited')
            #self.fields.pop('is_in_shopping_cart')

    def validate_cooking_time(self, value):
        if value >= 1:
            return value
        else:
            raise ValidationError(
                'Время готовки должно быть больше либо равно 1')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        try:
            Favorite.objects.get(user=user, recipe=obj)
            return True
        except Favorite.DoesNotExist:
            return False


class RecipeUserSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
                     tuple(User.REQUIRED_FIELDS)) + (
                     'email',
                     'id',
                     'is_subscribed',
                     'recipes',
                     'recipes_count',
                     'avatar',
                 )
        read_only_fields = ['is_subscribed',
                            'id',
                            'email',
                            'recipes',
                            'recipes_count']

    def __init__(self, *args, **kwargs):
        limit_recipes = kwargs.pop('limit_recipes', None)
        super().__init__(*args, **kwargs)

        if limit_recipes:
            limit_recipes = self.context.get('limit_recipes', None)

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit', obj.recipes.count())
        recipes = obj.recipes.all()[:int(limit)]
        return RecipeSerializer(recipes,
                                exclude_text=True,
                                exclude_ingredients=True,
                                exclude_author=True,
                                exclude_serializer_method=True,
                                many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


#TODO: реализовать сериализатор подписки
class SubscriptionSerializer(Serializer):
    user = RecipeUserSerializer()

    class Meta:
        fields = '__all__'

    def get_id(self, obj, request):
        return -1
