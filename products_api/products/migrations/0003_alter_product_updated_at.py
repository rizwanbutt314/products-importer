# Generated by Django 4.0.2 on 2022-02-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_created_at_product_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(blank=True, help_text='Updated DateTime of product', null=True),
        ),
    ]
