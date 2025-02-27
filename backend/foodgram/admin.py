from django.contrib import admin
from django.db.models import Count

from foodgram.models import (User,
                             Recipe,
                             Ingredient,
                             RecipeIngredient,
                             Favorite,
                             ShopList,
                             ShortLink,
                             Subscription)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribed_to',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'avatar', 'is_staff')
    search_fields = ('username', 'email', 'first_name')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

    def get_ingredient(self, obj):
        return f'{obj.ingredient} + {obj.ingredient.measurement_unit}'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'get_author_name', 'favorite_count')
    search_fields = ('author__first_name', 'name',)
    readonly_fields = ('favorite_count',)

    def get_author_name(self, obj):
        return obj.author.first_name

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count('favorite'))
        return queryset

    def favorite_count(self, obj):
        return obj.favorite_count

    def get_ingredients(self, obj):
        return ", ".join(ingredient.name for ingredient in obj.ingredients.all())

    get_ingredients.short_description = 'Ингредиенты'
    favorite_count.short_description = 'Добавлений в избранное'
    get_author_name.short_description = 'Имя автора'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShopList)
class ShopListAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_recipes')

    def get_recipes(self, obj):
        return ", ".join(recipe.name for recipe in obj.recipes.all())


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'hashid')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
