import imp
from django.urls import re_path
from products import views


urlpatterns = [
    re_path(r'^$', views.APIIndex.as_view(), name='api_index'),
]