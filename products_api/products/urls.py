import imp
from django.urls import re_path
from products import views


urlpatterns = [
    re_path(r'^$', views.APIIndex.as_view(), name='api_index'),
    re_path(r'^(?P<pk>\d+)/?$', views.APIDetail.as_view(), name='api_detail'),
    re_path(r'^upload/$', views.APIUploadProducts.as_view(), name='api_products_upload'),
    re_path(r'^upload-progress/$', views.UploadProgress.as_view(), name='upload_progress'),
]