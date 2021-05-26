"""crf2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import include, path
from django.views.generic import TemplateView

admin.site.site_header = "Course Request Form Administration"
admin.site.site_title = "ADMIN: Site Request"
# use re path to validate urls
# https://docs.djangoproject.com/en/2.1/topics/http/urls/#using-regular-expressions


# handler404 = 'course.views.not_found'
# handler500 = 'course.views.server_error'
# handler403 = 'course.views.permission_denied'
# handler400 = 'course.views.bad_request'


urlpatterns = [
    #    url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("", include("course.urls")),
]
# urlpatterns = [path('siterequest/', include(urlpatterns))]

# path('course', CourseView.as_view()),
