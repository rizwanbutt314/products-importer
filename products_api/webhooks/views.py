from rest_framework import mixins, generics

from products.models import WebHook
from .serializers import WebHooksSerializer


class APIIndex(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               generics.GenericAPIView):
    serializer_class = WebHooksSerializer
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
