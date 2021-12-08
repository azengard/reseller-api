from rest_framework.exceptions import APIException

from rest_framework import status


class PurchaseModifyForbiddenException(APIException):
    """Cannot modify a purchase when it's status is not validating"""
    status_code = status.HTTP_403_FORBIDDEN
    message_code = 'purchase_forbidden_modify_exception'
    message_text = "Can't modify a purchase when it's status isn't 'validating'"
