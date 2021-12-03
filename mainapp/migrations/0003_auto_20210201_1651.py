# Generated by Django 2.2 on 2021-02-01 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20210201_1559'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name'], 'verbose_name': 'продукт', 'verbose_name_plural': 'продукты'},
        ),
        migrations.AlterModelOptions(
            name='productcategory',
            options={'ordering': ['name'], 'verbose_name': 'категория продукта', 'verbose_name_plural': 'категории продуктов'},
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=type, upload_to='products_images'),
        ),
    ]