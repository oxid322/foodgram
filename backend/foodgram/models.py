from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField('Имя',
                                  max_length=150,
                                  blank=False,
                                  null=False)
    last_name = models.CharField('Фамилия',
                                 max_length=150,
                                 blank=False,
                                 null=False)
    avatar = models.ImageField('Аватар',
                               upload_to='avatars/',
                               blank=True,
                               default='')
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']
    USERNAME_FIELD = 'email'


class Subscription(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subcriptions')
    subscribed_to = models.ForeignKey(User,
                                      related_name='subscribers',
                                      on_delete=models.CASCADE)


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    def __str__(self):
        return self.name + ', ' + self.measurement_unit


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    name = models.CharField("Название", max_length=256)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингридиенты')
    cooking_time = models.PositiveIntegerField('Время приготовления')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Вспомогательная модель рецепта"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество',
                                 null=False,
                                 blank=False,
                                 default=0)

    def __str__(self):
        return f"{self.amount} {self.ingredient.measurement_unit} {self.ingredient.name} для {self.recipe.name}"


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorite')

    def __str__(self):
        return f"{self.user.username} {self.recipe.name}"


class ShopList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe,
                                     related_name='shop_lists',
                                     blank=True)

    def __str__(self):
        return f"Shopping List for {self.user.username}"

    class Meta:
        unique_together = ('user',)
