from django.db import models


class WebHook(models.Model):
    """ WebHook model """

    url = models.TextField(
        blank=True,
        help_text="WebHook URL")
    active = models.BooleanField(default=True)
