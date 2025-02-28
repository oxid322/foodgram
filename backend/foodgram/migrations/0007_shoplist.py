# Generated by Django 5.1.5 on 2025-02-23 03:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0006_favorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipes', models.ManyToManyField(blank=True, null=True, related_name='shop_lists', to='foodgram.recipe')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user',)},
            },
        ),
    ]
