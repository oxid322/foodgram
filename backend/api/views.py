from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (UpdateModelMixin,
                                   DestroyModelMixin,
                                   CreateModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet

from foodgram.models import Subscription, Recipe, Ingredient, Favorite
from .pagination import CustomPagination
from .serializers import (CustomUserSerializer,
                          SubscriptionSerializer,
                          AvatarSerializer,
                          ChangePasswordSerializer,
                          RecipeSerializer,
                          IngredientSerializer,
                          RecipeUserSerializer)

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


class SubscriptionViewSet(ListModelMixin,
                          CreateModelMixin,
                          DestroyModelMixin,
                          GenericViewSet):
    serializer_class = RecipeUserSerializer
    queryset = Subscription.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        # if serializer.is_valid(raise_exception=False):
        sub_to = None
        try:
            sub_to = User.objects.get(id=self.kwargs['id'])
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
            serializer = self.get_serializer(sub_to)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']
        user = self.request.user
        try:
            sub_to = User.objects.get(id=id)
            try:
                sub = Subscription.objects.get(user=user, subscribed_to=sub_to)
                sub.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response({'detail': 'Вы не подписаны на пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'detail': 'Пользователя не существует'}, status=status.HTTP_404_NOT_FOUND)


class ListSubViewSet(ListModelMixin, GenericViewSet):
    serializer_class = RecipeUserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        limit = self.request.query_params.get('recipes_limit', None)
        queryset = self.get_queryset().filter(subscribers__user=self.request.user)

        serializer = self.get_serializer(queryset,
                                         context={'request': request},
                                         many=True,
                                         limit_recipes=limit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def paginator(self):
    # TODO: Пагинация не работает


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
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FavoriteViewSet(DestroyModelMixin,
                      CreateModelMixin,
                      GenericViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.get_queryset()
        try:
            recipe = queryset.get(id=self.kwargs['id'])
            try:
                Favorite.objects.get(user=user, recipe=recipe)
                return Response({'detail': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                serializer = self.get_serializer(instance=recipe,
                                                 exclude_text=True,
                                                 exclude_ingredients=True,
                                                 exclude_author=True,
                                                 exclude_serializer_method=True)
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(serializer.data, status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']
        user = self.request.user
        try:
            recipe = Recipe.objects.get(id=id)
            try:
                fav = Favorite.objects.get(user=user, recipe=recipe)
                fav.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response({'detail': 'Рецепта нет в избранном'})
        except ObjectDoesNotExist:
            return Response({'detail': 'Рецепт не существует'}, status=status.HTTP_404_NOT_FOUND)
