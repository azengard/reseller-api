from django.urls import path

from .viewsets import hello_world


urlpatterns = [
    path('', hello_world)
]
