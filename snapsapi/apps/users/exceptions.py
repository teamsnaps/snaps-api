from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class UserNotExistException(APIException):
    """
    Custom exception for cases where a user is not found.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('The specified user could not be found.')
    default_code = 'user_not_found'
