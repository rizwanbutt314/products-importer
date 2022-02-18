from rest_framework import serializers

from webhooks.models import WebHook


class WebHooksSerializer(serializers.ModelSerializer):

    class Meta:
        model = WebHook
        fields = '__all__'
