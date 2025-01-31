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
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']


class Subcription(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subcriptions')
    subscribed_to = models.ForeignKey(User,
                                      related_name='subscribers',
                                      on_delete=models.CASCADE)

