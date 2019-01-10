from django.conf.urls import url
from django_app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
