from rest_framework.routers import DefaultRouter

from .viewsets import PurchaseViewSet

router = DefaultRouter()
router.register('', PurchaseViewSet, basename='purchase')
urlpatterns = router.urls
