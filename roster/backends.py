from django.contrib.auth.backends import ModelBackend
from .models import UserAccount

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserAccount.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserAccount.DoesNotExist:
            return None