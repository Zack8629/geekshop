import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geekshop.settings')

import django

django.setup()

from django.db import connection
from django.db.models import Q

from mainapp.models import Product
from mainapp.views import db_profile_by_type


def sample_1():
    test_products = Product.objects.filter(
        Q(category__name='офис') |
        Q(category__name='модерн')
    ).select_related('category')

    print(test_products)

    db_profile_by_type('learn db', '', connection.queries)


def sample_2():
    from datetime import timedelta
    from django.db.models import F, When, Case, IntegerField, DecimalField
    from ordersapp.models import OrderItem

    ACTION_1 = 1
    ACTION_2 = 2
    ACTION_EXPIRED = 3

    action_1__dt = timedelta(hours=12)
    action_2__dt = timedelta(days=1)

    action_1_disc = 0.3
    action_2_disc = 0.15
    action_exp_disc = 0.05

    action_1__cond = Q(
        order__update_dt__lte=F('order__add_dt') + action_1__dt
    )
    action_2__cond = Q(
        order__update_dt__gt=F('order__add_dt') + action_1__dt
    ) & Q(
        order__update_dt__lte=F('order__add_dt') + action_2__dt
    )
    action_exp__cond = Q(
        order__update_dt__gt=F('order__add_dt') + action_2__dt
    )

    action_1__order = When(action_1__cond, then=ACTION_1)
    action_2__order = When(action_2__cond, then=ACTION_2)
    action_expired__order = When(action_exp__cond, then=ACTION_EXPIRED)

    action_1__price = When(action_1__cond,
                           then=F('product__price') * F('quantity') * action_1_disc)
    action_2__price = When(action_2__cond,
                           then=F('product__price') * F('quantity') * -action_2_disc)
    action_expired__price = When(action_exp__cond,
                                 then=F('product__price') * F('quantity') * action_exp_disc)

    best_orderitems = OrderItem.objects.annotate(
        action_order=Case(
            action_1__order,
            action_2__order,
            action_expired__order,
            output_field=IntegerField(),
        )).annotate(
        discount=Case(
            action_1__price,
            action_2__price,
            action_expired__price,
            output_field=DecimalField(),
        )).order_by('action_order', 'discount'). \
        select_related('order', 'product')

    for orderitem in best_orderitems:
        print(f'{orderitem.action_order:2}: заказ №{orderitem.pk:3}:\
               {orderitem.product.name:35}: скидка\
               {abs(orderitem.discount):8.2f} руб. | \
               {orderitem.order.update_dt - orderitem.order.add_dt}')


if __name__ == '__main__':
    sample_1()
    sample_2()
