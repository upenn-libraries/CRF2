from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import User
from course.models import Profile


class CustomRemoteUserMiddleware(RemoteUserMiddleware):
    def configure_user(request, user):
        meta = request.META
        try:
            user.update(
                first_name=meta["givenName"], last_name=meta["sn"], email=meta["mail"]
            )
            Profile.objects.update_or_create(user=user, penn_id=meta["penn_id"])
        except:
            # fail silently
            pass
