# Generated by Django 5.1.5 on 2025-02-24 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0008_alter_favorite_recipe_alter_favorite_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=0, verbose_name='Количество'),
        ),
    ]
