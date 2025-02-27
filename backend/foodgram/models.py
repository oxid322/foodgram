from hashids import Hashids

from django.db import models
from django.contrib.auth.models import AbstractUser

hashids = Hashids(salt='pivo', min_length=3)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=150,
                                  blank=False,
                                  null=False)
    last_name = models.CharField(verbose_name='Фамилия',
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
                             related_name='subcriptions',
                             verbose_name='Пользователь',
                             help_text='Подписчик')
    subscribed_to = models.ForeignKey(User,
                                      related_name='subscribers',
                                      on_delete=models.CASCADE,
                                      verbose_name='Пользователь',
                                      help_text='Цель подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    def __str__(self):
        return self.name + ', ' + self.measurement_unit

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    name = models.CharField("Название", max_length=256)
    image = models.ImageField(upload_to='recipes/', verbose_name='Картинка')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингридиенты')
    cooking_time = models.PositiveIntegerField('Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_short_link(self):
        hashid = hashids.encode(self.id)
        return ShortLink.objects.get_or_create(recipe=self, hashid=hashid)[0]


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

    class Meta:
        verbose_name = 'Рецепт ингредиент'
        verbose_name_plural = 'Рецепт ингредиенты'


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorite',
                               verbose_name='Рецепт')

    def __str__(self):
        return f"{self.user.username} {self.recipe.name}"

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShopList(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                verbose_name='Пользователь')
    recipes = models.ManyToManyField(Recipe,
                                     related_name='shop_lists',
                                     blank=True,
                                     verbose_name='Рецепт')

    def __str__(self):
        return f"Shopping List for {self.user.username}"

    class Meta:
        unique_together = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class ShortLink(models.Model):
    recipe = models.OneToOneField(Recipe,
                                  on_delete=models.CASCADE,
                                  verbose_name='Рецепт')
    hashid = models.CharField(verbose_name='Хэш-идентификатор',
                              max_length=32,
                              unique=True)

    def __str__(self):
        return f'Short Link for {self.recipe.name}'

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
