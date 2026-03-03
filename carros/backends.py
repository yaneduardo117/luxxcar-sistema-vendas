from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailLoginBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Aqui, o "username" que vem do formulário HTML será na verdade o E-mail digitado
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None