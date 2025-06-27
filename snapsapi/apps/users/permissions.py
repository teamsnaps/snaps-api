from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    """
    Allows access only to authenticated users who are active and not deleted.
    """
    message = 'The user is inactive or has been deleted.'

    def has_permission(self, request, view):
        """
        Check if the user associated with the request is active.
        """
        # IsAuthenticated permission class should be used before this,
        # so request.user is expected to be an authenticated user instance.
        return request.user and request.user.is_active and not request.user.is_deleted


# (If you have IsProfileOwner from previous examples, keep it here as well)
class IsProfileOwner(BasePermission):
    """
    Allows access only to the owner of the profile.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user of the profile object is the same as the request user.
        'obj' here is a Profile instance.
        """
        return obj.user == request.user
