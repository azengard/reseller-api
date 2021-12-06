from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.api.reseller.serializers import ResellerSerializer


class ResellerViewSet(CreateModelMixin, GenericViewSet):
    authentication_classes = ()
    permission_classes = ()

    serializer_class = ResellerSerializer
