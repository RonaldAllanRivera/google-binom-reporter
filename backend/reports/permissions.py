from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from .models import GoogleAccount

class IsGoogleOrSuperuser(BasePermission):
    """
    Allows access only to users authenticated via Google OAuth (exists in GoogleAccount)
    or Django superusers (admin login).
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        # Allow Django superusers
        if user and user.is_authenticated and getattr(user, 'is_superuser', False):
            return True
        # Allow Google-authenticated users (session/cookie/email)
        # Check for Google-authenticated user via session
        if user and user.is_authenticated and hasattr(user, 'email') and user.email:
            try:
                # Verify that the authenticated user's email is registered for Google services
                if GoogleAccount.objects.filter(user_email=user.email).exists():
                    return True
            except GoogleAccount.DoesNotExist:
                pass
        return False
