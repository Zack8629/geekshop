from django.contrib.auth import get_user_model
from django.db import models

from mainapp.models import Product


class Basket(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='basket')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('количество', default=0)
    datetime_add = models.DateTimeField('время добавления', auto_now_add=True)
    datetime_upd = models.DateTimeField('время обновления', auto_now=True)

    @property
    def product_cost(self):
        return self.product.price * self.quantity
