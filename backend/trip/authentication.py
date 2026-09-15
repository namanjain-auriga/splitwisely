from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        user = User.objects.filter(email__iexact=username).first() or User.objects.filter(username=username).first()
        if user and user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None