from django.contrib import admin
from foodgram.models import (User,
                             Recipe,
                             Ingredient, RecipeIngredient)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'avatar', 'is_staff')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient

    extra = 1

    def get_ingredient(self, obj):
        return f'{obj.ingredient} + {obj.ingredient.measurement_unit}'




@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('author', 'name', 'image', 'text', 'cooking_time', 'get_ingredients')

    def get_ingredients(self, obj):
        return ", ".join(ingredient.name for ingredient in obj.ingredients.all())

    get_ingredients.short_description = 'Ингредиенты'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')



