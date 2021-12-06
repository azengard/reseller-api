from django.urls import path, include


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),

    path('reseller/', include('apps.api.reseller.urls')),
    path('purchase/', include('apps.api.purchase.urls')),
]
