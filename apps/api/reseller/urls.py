from rest_framework.routers import DefaultRouter

from .viewsets import ResellerViewSet

router = DefaultRouter()
router.register('', ResellerViewSet, basename='reseller')
urlpatterns = router.urls
