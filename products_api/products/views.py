from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import mixins, generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse, StreamingHttpResponse

from products.models import Product
from .serializers import ProductsSerializer


class APIIndex(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               generics.GenericAPIView):
    serializer_class = ProductsSerializer
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('sku', 'name', 'active', 'description')

    def get_queryset(self):
        return Product.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs.exists():
            qs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return JsonResponse({"error": "no product found"}, status=status.HTTP_404_NOT_FOUND)


class APIDetail(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                generics.GenericAPIView):
    serializer_class = ProductsSerializer

    def get_queryset(self):
        return Product.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class APIUploadProducts(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        _file = request.FILES.get("File")
        return Response({'success': True}, status=status.HTTP_200_OK)


class UploadProgress(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        import time
        upload_id = request.GET.get('upload_id', None)
        if not upload_id:
            return Response({"error": "upload_id is required as query param"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"{request.META['REMOTE_ADDR']}_{upload_id}"
        data = cache.get(cache_key)
        if not data:
            return Response({"error": "invalid upload_id"}, status=status.HTTP_404_NOT_FOUND)

        def stream():
            while True:
                time.sleep(2)
                data = cache.get(cache_key)
                yield f"{data['uploaded_percentage']}"

        return StreamingHttpResponse(stream(), content_type='text/event-stream')
