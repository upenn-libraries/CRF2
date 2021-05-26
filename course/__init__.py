from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

# default_app_config = '.apps.CourseAppConfig'


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    print("User ", user.username, " just logged in")
    request.session["on_behalf_of"] = ""
    # Display custom messgage !
    messages.info(request, "Welcome!")


# django.contrib.auth.logout() calls flush() which
# Deletes the current session data from the session and deletes the session cookie.

# @receiver(user_logged_out)
# def on_logout(sender, user, request, **kwargs):


# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ("celery_app",)


"""

  <!-- this may be computationally more complex than needed ... may be slowing things down -->
{% if '/accounts/login/' in request.META.HTTP_REFERER %}

<div class="alert alert-warning alert-dismissible fade show" role="alert" style="margin:10px;z-index:inherit;">
<h4 class="alert-heading">Heading!</h4>
<!--<strong>strong text!</strong>-->
<p>
Courses taught through Graduate School of Education (GSE), Penn Law, The School of Veterinary Medicine and Wharton cannot be requested through our Course Request Form.
</p>
<p> For further assistance setting up your course site please contact the appropriate address below.  </p>
<ul>
<li>Graduate School of Education (GSE): gse-help@lists.upenn.edu | GSE Site Request Form </li>
<li>Law: itshelp@law.upenn.edu </li>
<li>Veterinary Medicine: phl-help@vet.upenn.edu </li>
<li>Wharton: courseware@wharton.upenn.edu </li>
</ul>
<hr>
<p class="mb-0">If you believe you are receiving this message in error, please contact canvas@pobox.upenn.edu</p>
<div class="close" data-dismiss="alert" aria-label="Close">
<span aria-hidden="true"><i class="fas fa-times"></i></span>
</div>
</div>
{% endif %}
"""
