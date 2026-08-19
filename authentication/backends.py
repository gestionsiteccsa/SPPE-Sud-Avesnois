from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        candidates = list(UserModel._default_manager.filter(email__iexact=username)[:2])
        if len(candidates) != 1:
            UserModel().set_password(password)
            return None
        user = candidates[0]
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
