# Generated by Django 5.1.5 on 2025-01-31 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0002_subcription'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subcription',
            new_name='Subscription',
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, default='', upload_to='avatars/', verbose_name='Аватар'),
        ),
    ]
