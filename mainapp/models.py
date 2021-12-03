from django.db import models


class ProductCategory(models.Model):
    name = models.CharField('имя', max_length=64)
    description = models.TextField('описание', blank=True)
    short_description = models.CharField('краткое описание', max_length=200, blank=True)
    is_active = models.BooleanField('активность', db_index=True, default=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'категория продукта'
        verbose_name_plural = 'категории продуктов'
        ordering = ['name']

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(using=using)


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField('имя', max_length=64)
    description = models.TextField('описание', blank=True)
    short_description = models.CharField('краткое описание', max_length=200, blank=True)
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField('количество на складе', default=0)
    image = models.ImageField(upload_to='products_images', blank=type)
    is_active = models.BooleanField('активность', db_index=True, default=True)

    def __str__(self):
        return f'{self.name} ({self.category.name})'

    @classmethod
    def get_items(cls):
        return cls.objects.select_related('category').filter(is_active=True,
                                                             category__is_active=True)

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        ordering = ['name']
