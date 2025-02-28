# Generated by Django 5.1.5 on 2025-02-26 15:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0010_shortlink'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Рецепт ингредиент', 'verbose_name_plural': 'Рецепт ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='shoplist',
            options={'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='shortlink',
            options={'verbose_name': 'Короткая ссылка', 'verbose_name_plural': 'Короткие ссылки'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='shoplist',
            name='recipes',
            field=models.ManyToManyField(blank=True, related_name='shop_lists', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='shoplist',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='shortlink',
            name='hashid',
            field=models.CharField(max_length=32, unique=True, verbose_name='Хэш-идентификатор'),
        ),
        migrations.AlterField(
            model_name='shortlink',
            name='recipe',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='foodgram.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='subscribed_to',
            field=models.ForeignKey(help_text='Цель подписки', on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(help_text='Подписчик', on_delete=django.db.models.deletion.CASCADE, related_name='subcriptions', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
