from datetime import timedelta
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        # Check expiration (48 hours)
        if token.created < timezone.now() - timedelta(hours=48):
            token.delete() # Optional: auto delete expired token
            raise exceptions.AuthenticationFailed('Token has expired')

        return (token.user, token)
