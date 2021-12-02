from django.urls import path, include


urlpatterns = [
    path('reseller/', include('apps.api.reseller.urls')),
]
