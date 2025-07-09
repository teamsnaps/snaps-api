from rest_framework.permissions import BasePermission


class IsCommentOwner(BasePermission):
    """
    Allows access only to the owner of the profile.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user of the profile object is the same as the request user.
        'obj' here is a Profile instance.
        """
        return obj.user == request.user
