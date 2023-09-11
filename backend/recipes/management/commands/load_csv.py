import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу.'

    def handle(self, *args, **options):
        with open(os.path.join(DATA_ROOT, options['filename']),
                  'r', encoding='utf-8') as file:
            reader_data = csv.reader(file)
            for name, measurement_unit in reader_data:
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
