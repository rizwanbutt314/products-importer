from rest_framework import mixins, generics

from products.models import WebHook
from .serializers import WebHooksSerializer


class APIIndex(mixins.CreateModelMixin,
               generics.GenericAPIView):
    serializer_class = WebHooksSerializer
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
