from django.db import models


class Product(models.Model):
    """ Product model """

    name = models.CharField(
        max_length=255,
        unique=False,
        help_text="Name")
    sku = models.CharField(
        max_length=255,
        unique=True,
        help_text="Product SKU")
    description = models.TextField(
        blank=True,
        help_text="Product description")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
