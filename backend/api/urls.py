from django.urls import path, include
from rest_framework import routers
from .views import (AvatarViewSet,
                    MyUserViewSet,
                    RecipeViewSet,
                    IngredientViewSet,
                    DownloadShoppingList)

app_name = 'foodgram_api'
router = routers.DefaultRouter()
router.register(r'users', MyUserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)

# router.register(r'/me/avatar', AvatarViewSet, basename='avatar')


urlpatterns = [
    path('users/me/avatar/', AvatarViewSet.as_view({'put': 'update',
                                                    'delete': 'destroy'}), name='avatar'),
    # path('recipes/<int:id>/shopping_cart/',
    #      ShopListView.as_view(),
    #      name='subscribe'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingList.as_view(),
         name='download_shopping_cart'),

    path('', include(router.urls)),

]
