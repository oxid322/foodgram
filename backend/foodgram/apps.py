from django.apps import AppConfig
from django.db.models.signals import post_migrate


def load_fixtures(sender, **kwargs):
    from django.core.management import call_command
    call_command('loaddata', 'fixture.json')


class FoodgramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodgram'
    verbose_name = 'Фудграм'

    def ready(self):
        post_migrate.connect(load_fixtures, sender=self)
