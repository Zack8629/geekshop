from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property

from mainapp.models import Product


class Order(models.Model):
    STATUS_FORMING = 'F'
    STATUS_PAID = 'P'
    STATUS_SENDED = 'S'
    STATUS_RECEIVED = 'R'
    STATUS_DELAYED = 'D'

    STATUS_CHOICES = (
        (STATUS_FORMING, 'формируется'),
        (STATUS_PAID, 'оплачен'),
        (STATUS_SENDED, 'отправлен'),
        (STATUS_RECEIVED, 'получен'),
        (STATUS_DELAYED, 'отменен'),
    )

    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='orders')
    add_dt = models.DateTimeField('время', auto_now_add=True)
    update_dt = models.DateTimeField('время', auto_now=True)
    status = models.CharField('статус', max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_FORMING)
    is_active = models.BooleanField(verbose_name='активен',
                                    db_index=True,
                                    default=True)

    @cached_property
    def is_forming(self):
        return self.status == self.STATUS_FORMING

    @cached_property
    def total_quantity(self):
        return sum(map(lambda x: x.quantity, self.items.all()))

    @cached_property
    def total_cost(self):
        return sum(map(lambda x: x.product_cost, self.items.all()))

    @cached_property
    def summary(self):
        items = self.items.all()
        return {
            'total_quantity': sum(map(lambda x: x.quantity, items)),
            'total_cost': sum(map(lambda x: x.product_cost, items))
        }

    def delete(self, using=None, keep_parents=False):
        for item in self.items.all():
            item.product.quantity += item.quantity
            item.product.save()
        self.is_active = False
        self.save()

    class Meta:
        ordering = ('-add_dt',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItemManager(models.QuerySet):
    def delete(self):
        print('OrderItem QS delete')


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('количество', default=0)
    add_dt = models.DateTimeField('время', auto_now_add=True)
    update_dt = models.DateTimeField('время', auto_now=True)

    @cached_property
    def product_cost(self):
        return self.product.price * self.quantity

    @classmethod
    def get_item(cls, pk):
        return cls.objects.select_related('product').filter(pk=pk).first()
