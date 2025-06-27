from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class FollowYourselfException(APIException):
    """
    Custom exception for cases when the user attempts to follow themselves.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Users cannot follow themselves.')
    default_code = 'follow_yourself_error'
