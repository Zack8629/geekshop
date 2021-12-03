from django.urls import path

import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.index, name='index'),
    path('catalog/', mainapp.products, name='products'),
    path('contact/', mainapp.contact, name='contact'),
    path('snake/', mainapp.snake, name='snake'),

    path('category/<int:pk>/', mainapp.category, name='category'),
    path('product/<int:pk>/', mainapp.product_page, name='product_page'),
    path('product/<int:pk>/price/', mainapp.get_product_price),
]
