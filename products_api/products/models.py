from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Updated DateTime of product")

    class Meta:
        ordering = ['-id']


class ProcessedFileHistory(models.Model):
    """ Processed File History model """

    sha256 = models.CharField(max_length=64, unique=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Product)
def notify_webhooks_on_product_product_update_or_create(sender, instance, **kwargs):
    from .tasks import notify_webhooks
    # notify webhooks using background task
    notify_webhooks.delay(instance.id)