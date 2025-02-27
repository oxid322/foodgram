import logging

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, PasswordSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField, CharField
from rest_framework.serializers import (ModelSerializer,
                                        Serializer,
                                        IntegerField,
                                        ValidationError)

from foodgram.models import Subscription, Ingredient, Recipe, RecipeIngredient, Favorite, ShopList

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomUserSerializer(UserCreateSerializer):
    """Кастомный сериализатор пользователя"""
    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(max_length=25500, required=False)

    class Meta:
        model = User
        fields = (('email', 'id') +
                  tuple(User.REQUIRED_FIELDS)) + (
                     'is_subscribed',
                     'avatar',
                 )
        read_only_fields = ['is_subscribed', 'id']

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

        if request.path == '/api/users/' and request.method == "POST":
            representation.pop('is_subscribed', None)
            representation.pop('avatar', None)

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
    avatar = Base64ImageField(max_length=25500, required=True)

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
    name = CharField(read_only=True)
    measurement_unit = CharField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class RecipeSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True,
                                       read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=10 ** 6,
                             required=True)
    cooking_time = IntegerField(required=True)
    text = CharField(required=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def __init__(self, *args, **kwargs):
        # Убираем поле `author`, если передан параметр `exclude_author=True` и т д
        exclude_author = kwargs.pop('exclude_author', False)
        exclude_ingredients = kwargs.pop('exclude_ingredients',
                                         False)
        exclude_text = kwargs.pop('exclude_text', False)
        exclude_serializer_method = kwargs.pop('exclude_serializer_method', False)
        for_download = kwargs.pop('for_download', False)

        super().__init__(*args, **kwargs)
        if exclude_author:
            self.fields.pop('author')

        if exclude_ingredients:
            self.fields.pop('ingredients')

        if exclude_text:
            self.fields.pop('text')

        if exclude_serializer_method:
            self.fields.pop('is_favorited')
            self.fields.pop('is_in_shopping_cart')

    def validate_cooking_time(self, value):
        if value >= 1:
            return value
        else:
            raise ValidationError(
                'Время готовки должно быть больше либо равно 1')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            try:
                Favorite.objects.get(user=user, recipe=obj)
                return True
            except Favorite.DoesNotExist:
                return False
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            try:
                shop_list = ShopList.objects.get(user=user)
                if obj in shop_list.recipes.all():
                    return True
                return False
            except ShopList.DoesNotExist:
                return False
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


class _IngredientSerializer(ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    amount = IntegerField(required=True)
    id = IntegerField(required=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'amount')
        read_only_fields = ('ingredient',)

    def to_representation(self, instance):
        dic = {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount,
        }
        return dic

    def validate_amount(self, value):
        if value >= 1:
            return value
        raise ValidationError("Убедитесь, что это значение больше либо равно 1.")


class PostRecipeSerializer(RecipeSerializer):
    ingredients = _IngredientSerializer(many=True,
                                        source='recipeingredient_set',
                                        required=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'text',
                  'cooking_time',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  )
        read_only_fields = ['author']

    def create_ingredients_connections(self, recipe, ingredients):
        print(ingredients)
        for ingredient in ingredients:
            ing_id = ingredient.get('id')
            print(ing_id)
            ingredient_inst = Ingredient.objects.get(id=ing_id)
            ri = RecipeIngredient.objects.create(recipe=recipe,
                                                 ingredient=ingredient_inst,
                                                 amount=ingredient.get('amount'))

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredient_set')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients_connections(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('recipeingredient_set', None) is not None:
            ingredients = validated_data.pop('recipeingredient_set')
            instance.ingredients.clear()
            self.create_ingredients_connections(instance, ingredients)
            return super().update(instance, validated_data)
        raise ValidationError({'ingredients': 'Это поле обязательно.'})

    def to_representation(self, instance):
        i = 0
        representation = super().to_representation(instance)
        representation['ingredients'] = _IngredientSerializer(instance.recipeingredient_set.all(),
                                                              many=True).data
        # for ingredient in representation['ingredients']:
        #     ingredient['id'] = i
        #     i += 1
        return representation

    def validate_ingredients(self, value):
        if value:
            ingredient_ids = [item['id'] for item in value]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise ValidationError('Ингредиенты не должны повторяться')
            return value
        raise ValidationError('Это поле обязательно для заполнения.')

    def validate_image(self, image):
        if image:
            return image
        raise ValidationError('Это поле обязательно для заполнения.')


class SubscriptionSerializer(Serializer):
    user = RecipeUserSerializer()

    class Meta:
        fields = '__all__'

    def get_id(self, obj, request):
        return -1


class ShopListSerializer(ModelSerializer):
    recipes = SerializerMethodField()

    class Meta:
        model = ShopList
        fields = ('recipes',)

    def get_recipes(self, obj):
        recipes = RecipeSerializer(obj.recipes.all(), many=True).data
        result = {

        }
