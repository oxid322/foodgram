import logging

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from hashids import Hashids
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (UpdateModelMixin,
                                   DestroyModelMixin)
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (ModelViewSet,
                                     GenericViewSet,
                                     ReadOnlyModelViewSet)

from foodgram.models import (Subscription,
                             Recipe,
                             Ingredient,
                             Favorite,
                             ShopList,
                             RecipeIngredient,
                             ShortLink)
from .pagination import CustomPagination
from .permisions import IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer,
                          AvatarSerializer,
                          ChangePasswordSerializer,
                          RecipeSerializer,
                          IngredientSerializer,
                          RecipeUserSerializer,
                          PostRecipeSerializer)

hashids = Hashids(salt='pivo', min_length=3)

logger = logging.getLogger(__name__)

User = get_user_model()


class MyUserViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_instance(self):
        return self.request.user

    @action(['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.get_object = self.get_instance
            return self.retrieve(request, *args, **kwargs)
        return Response({'detail': 'Пользователь не авторизован'},
                        status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['POST'], detail=False)
    def set_password(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        limit = self.request.query_params.get('recipes_limit', None)
        queryset = self.get_queryset().filter(subscribers__user=self.request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecipeUserSerializer(page, many=True, context={'request': self.request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeUserSerializer(queryset,
                                          context={'request': self.request},
                                          many=True,
                                          limit_recipes=limit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            if request.method == 'POST':
                user = self.request.user
                sub_to = None
                try:
                    sub_to = User.objects.get(id=pk)
                    Subscription.objects.get(user=user, subscribed_to=sub_to)
                    return Response({'detail': 'Подписка уже существует'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    if not sub_to:
                        return Response({'detail': 'Пользователя не существует'},
                                        status=status.HTTP_404_NOT_FOUND)
                    if user == sub_to:
                        return Response({'detail': 'Нельзя подписаться на самого себя'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    sub = Subscription.objects.create(user=user, subscribed_to=sub_to)
                    serializer = RecipeUserSerializer(sub_to, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                user = self.request.user
                try:
                    sub_to = User.objects.get(id=pk)
                    try:
                        sub = Subscription.objects.get(user=user, subscribed_to=sub_to)
                        sub.delete()
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    except ObjectDoesNotExist:
                        return Response({'detail': 'Вы не подписаны на пользователя'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'detail': 'Пользователя не существует'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'detail': 'Не удается авторизоваться с проведенными данными.'},
                status=status.HTTP_401_UNAUTHORIZED)


class AvatarViewSet(UpdateModelMixin,
                    DestroyModelMixin,
                    GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        instance = self.get_queryset().get(id=self.request.user.id)
        serializer = AvatarSerializer(instance=instance,
                                      data=request.data,
                                      partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    serializer_class = PostRecipeSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]

    def list(self, request, *args, **kwargs):
        is_favorited: str = None
        is_in_shopping_cart: str = None
        user = request.user
        queryset: QuerySet[Recipe] = Recipe.objects.all()
        query_params = self.request.query_params
        author: str = query_params.get('author', None)
        if user.is_authenticated:
            is_favorited = query_params.get('is_favorited', None)
            is_in_shopping_cart = query_params.get('is_in_shopping_cart', None)

        if author:
            if author.isdigit():
                author_id = int(author)
                queryset = queryset.filter(author__id=author_id)
        if is_favorited:
            if is_favorited.isdigit():
                recipes = Favorite.objects.filter(user=user)
                queryset = queryset.filter(favorite__in=recipes)
        if is_in_shopping_cart:
            if is_in_shopping_cart.isdigit():
                shop_list = ShopList.objects.get_or_create(user=user)[0]
                logger.debug(shop_list.recipes.all())
                queryset = queryset.filter(shop_lists=shop_list)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        recipe = serializer.save()
        hashid = hashids.encode(recipe.id)
        ShortLink.objects.create(recipe=recipe, hashid=hashid)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            ingredients_data = request.data.get("ingredients", [])
            non_exist_ingredients = self.__check_ingredients_exist(ingredients_data)
            if non_exist_ingredients:
                return non_exist_ingredients
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({'detail': f'Метод /{request.method}/ не разрешен.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid():
            ingredients_data = request.data.get("ingredients", [])
            non_exist_ingredients = self.__check_ingredients_exist(ingredients_data)
            if non_exist_ingredients:
                return non_exist_ingredients
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def __check_ingredients_exist(self, ingredients):
        for ingredient in ingredients:
            id = int(ingredient.get("id", ''))
            if not Ingredient.objects.filter(id=id).exists():
                return Response({'detail': 'Ингредиент не существует'}, status=status.HTTP_400_BAD_REQUEST)
        return None

    @action(methods=['GET'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link_obj = recipe.get_short_link()
        short_link = f'http://localhost:8000/s/{short_link_obj.hashid}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            if request.method == 'POST':
                user = self.request.user
                queryset = self.get_queryset()
                try:
                    recipe = queryset.get(id=pk)
                    try:
                        Favorite.objects.get(user=user, recipe=recipe)
                        return Response({'detail': 'Рецепт уже в избранном'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    except ObjectDoesNotExist:
                        serializer = RecipeSerializer(instance=recipe,
                                                      exclude_text=True,
                                                      exclude_ingredients=True,
                                                      exclude_author=True,
                                                      exclude_serializer_method=True)
                        Favorite.objects.create(user=user, recipe=recipe)
                        return Response(serializer.data, status.HTTP_201_CREATED)
                except ObjectDoesNotExist:
                    return Response({'detail': 'Рецепт не найден'},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                user = self.request.user
                try:
                    recipe = Recipe.objects.get(id=pk)
                    try:
                        fav = Favorite.objects.get(user=user, recipe=recipe)
                        fav.delete()
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    except ObjectDoesNotExist:
                        return Response({'detail': 'Рецепта нет в избранном'}, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'detail': 'Рецепт не существует'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detil': 'Вы не авторизованы'}, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            if request.method == 'POST':
                user = self.request.user
                shoplist = ShopList.objects.get_or_create(user=user)[0]
                try:
                    recipe = Recipe.objects.get(id=pk)
                    if recipe not in shoplist.recipes.all():
                        shoplist.recipes.add(recipe)
                        shoplist.save()
                        serializer = RecipeSerializer(recipe,
                                                      exclude_serializer_method=True,
                                                      exclude_text=True,
                                                      exclude_ingredients=True,
                                                      exclude_author=True,
                                                      context={'request': self.request})
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    return Response({'detail': 'Рецепт уже есть в списке'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except Recipe.DoesNotExist:
                    return Response({'detail': f'Рецепт не с id={pk} не найден'},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                user = request.user
                shoplist = ShopList.objects.get_or_create(user=user)[0]
                try:
                    recipe = Recipe.objects.get(id=pk)
                    if recipe in shoplist.recipes.all():
                        shoplist.recipes.remove(recipe)
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    return Response({'detail': 'Рецепта нет в списке'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except Recipe.DoesNotExist:
                    return Response({'detail': f'Рецепт не с id={pk} не найден'},
                                    status=status.HTTP_404_NOT_FOUND)
        return Response({'detail: Вы не авторизованы'},
                        status=status.HTTP_401_UNAUTHORIZED)


class GetRecipeByShortLink(APIView):
    def get(self, request, hashid):
        short_link = get_object_or_404(ShortLink, hashid=hashid)
        recipe = short_link.recipe
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)

        if name:
            queryset = queryset.filter(name__istartswith=name)

        return queryset


class DownloadShoppingList(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        shop_list = ShopList.objects.get_or_create(user=user)[0]
        recipes = shop_list.recipes.all()
        ingredients_res = {}
        for recipe in recipes:
            ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                name_mes = f'{name} {unit}'
                if name_mes in ingredients_res:
                    ingredients_res[name_mes] += amount
                else:
                    ingredients_res[name_mes] = amount

        # Создаем текстовый файл
        file_content = "\n".join(f'{key}: {value}' for key, value in ingredients_res.items())
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        return response
