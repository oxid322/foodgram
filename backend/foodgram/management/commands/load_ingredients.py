import json
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient

class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Path to JSON file')

    def handle(self, *args, **options):
        filename = options['filename']
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                ingredient = Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'],
                )
                ingredient.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully added {ingredient.name}'))
