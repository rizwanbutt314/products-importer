from django.db import models
from django.core.validators import URLValidator


class WebHook(models.Model):
    """ WebHook model """

    url = models.TextField(
        validators=[URLValidator()],
        blank=True,
        help_text="WebHook URL")
    active = models.BooleanField(default=True)
