from django.urls import path, include
from rest_framework import routers
from .views import (AvatarViewSet,
                    MyUserViewSet,
                    SubscriptionViewSet,
                    RecipeViewSet,
                    IngredientViewSet)



app_name = 'foodgram_api'
router = routers.DefaultRouter()
router.register(r'users', MyUserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)

# router.register(r'/me/avatar', AvatarViewSet, basename='avatar')


urlpatterns = [
    path('users/me/avatar/', AvatarViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='avatar'),
    path('users/<int:id>/subscribe/',
         SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('', include(router.urls)),

]