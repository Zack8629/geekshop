from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView

from ordersapp.forms import OrderForm, OrderItemForm
from ordersapp.models import Order, OrderItem


class LoggedUserOnlyMixin:
    @method_decorator(user_passes_test(lambda user: user.is_authenticated))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OrderList(LoggedUserOnlyMixin, ListView):
    model = Order

    def get_queryset(self):
        return self.request.user.orders.all()


class OrderCreate(LoggedUserOnlyMixin, CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        OrderFormSet = inlineformset_factory(Order, OrderItem,
                                             form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST, self.request.FILES)
        else:
            context['form'].initial['user'] = self.request.user
            basket_items = self.request.user.basket.all()
            if basket_items and basket_items.count():
                OrderFormSet = inlineformset_factory(Order, OrderItem,
                                                     form=OrderItemForm,
                                                     extra=basket_items.count() + 1)
                formset = OrderFormSet()
                for form, basket_item in zip(formset.forms, basket_items):
                    form.initial['product'] = basket_item.product
                    form.initial['quantity'] = basket_item.quantity
            else:
                formset = OrderFormSet()

        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            order = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()
                self.request.user.basket.all().delete()

        if self.object.total_cost == 0:
            self.object.delete()

        return order


class OrderUpdate(LoggedUserOnlyMixin, UpdateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem,
                                             form=OrderItemForm, extra=1)
        if self.request.POST:
            formset = OrderFormSet(self.request.POST,
                                   self.request.FILES,
                                   instance=self.object)
        else:
            queryset = self.object.items.select_related('product')
            formset = OrderFormSet(instance=self.object, queryset=queryset)
            # formset = OrderFormSet(instance=self.object)
            for form in formset.forms:
                instance = form.instance
                if instance.pk:
                    form.initial['price'] = instance.product.price
        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            order = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.save()

        if self.object.total_cost == 0:
            self.object.delete()

        return order


# class Buy(LoggedUserOnlyMixin, UpdateView):
#     pass


class OrderDetail(LoggedUserOnlyMixin, DetailView):
    model = Order


class OrderDelete(LoggedUserOnlyMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('orders:index')


def order_forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.STATUS_PAID
    order.save()

    return HttpResponseRedirect(reverse('orders:index'))


@receiver(pre_save, sender=OrderItem)
def product_quantity_update_save(sender, update_fields, instance, **kwargs):
    print('orderitem save')
    if instance.pk:
        instance.product.quantity += sender.get_item(instance.pk).quantity - \
                                     instance.quantity

    else:
        instance.product.quantity -= instance.quantity
    instance.product.save()


@receiver(pre_delete, sender=OrderItem)
def product_quantity_update_delete(sender, instance, **kwargs):
    print('orderitem delete')
    instance.product.quantity += instance.quantity
    instance.product.save()


@receiver(pre_delete, sender=Order)
def product_quantity_update_delete(sender, instance, **kwargs):
    print('orderdelete')
