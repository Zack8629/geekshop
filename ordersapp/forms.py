from django import forms
from django.forms import HiddenInput

from mainapp.models import Product
from ordersapp.models import Order, OrderItem


class BaseOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'user':
                field.widget = HiddenInput()
            field.widget.attrs['class'] = 'form-control'


class OrderForm(BaseOrderForm):
    class Meta:
        model = Order
        fields = ('user',)


class OrderItemForm(BaseOrderForm):
    price = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        products = Product.get_items()
        self.fields['product'].queryset = products

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')
        if quantity > product.quantity:
            raise forms.ValidationError('на складе нет столько товара')
        return quantity

    class Meta:
        model = OrderItem
        fields = '__all__'
