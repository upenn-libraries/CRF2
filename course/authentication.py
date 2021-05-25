from django.contrib.auth.models import User
from course import utils

""""
Since we are doing SSO authentication we need to


idea from: https://stackoverflow.com/a/51994770/10969047
but that requires backend changes

doesnt require backend changes: https://stackoverflow.com/a/40894635/10969047
"""


class SSOLogin:
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(raw_password=password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
