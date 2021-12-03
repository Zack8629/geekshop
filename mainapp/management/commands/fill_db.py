import json

from django.core.management.base import BaseCommand

from authapp.models import ShopUser
from mainapp.models import Product, ProductCategory


def load_from_json(file_name):
    with open(file_name, encoding='utf-8') as infile:
        return json.load(infile)


class Command(BaseCommand):
    help = 'Fill data in db'

    def handle(self, *args, **options):
        items = load_from_json('mainapp/json/categories.json')
        for item in items:
            ProductCategory.objects.create(**item)

        items = load_from_json('mainapp/json/products.json')
        for item in items:
            category = ProductCategory.objects.get(name=item['category'])
            item['category'] = category
            Product.objects.create(**item)

        if not ShopUser.objects.filter(username='django').exists():
            ShopUser.objects.create_superuser('django', 'django@gb.local', 'geekbrains')
