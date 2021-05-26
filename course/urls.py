from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import TemplateView
from rest_framework import renderers
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from course import views
# from rest_framework.schemas import get_schema_view # new
from course.autocomplete import (CanvasSiteAutocomplete, SubjectAutocomplete,
                                 UserAutocomplete)

schema_view = get_swagger_view(title="Pastebin API")

import csv

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"courses", views.CourseViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"notices", views.NoticeViewSet)
router.register(r"requests", views.RequestViewSet)
router.register(r"schools", views.SchoolViewSet)
router.register(r"subjects", views.SubjectViewSet)
router.register(r"autoadds", views.AutoAddViewSet)
router.register(r"canvassites", views.CanvasSiteViewSet)
"""
The example above would generate the following URL patterns:

URL pattern: ^users/$ Name: 'user-list'
URL pattern: ^users/{pk}/$ Name: 'user-detail'
URL pattern: ^courses/$ Name: 'course-list'
URL pattern: ^courses/{pk}/$ Name: 'course-detail'

-list goes to list()
-detail goes to retrieve()

This is fine because I want the API to be very generic

"""
# URL SHOULD REALLY USE REGEX
# SRS_SECTION_REGEX = re.compile(
#    r'^(?P<subject>[A-Z]{2,4})(?P<course_number>\d{3}|)-?(?P<section_number>\d{3}|)-(?P<term>20[01][0-9][ABC])$')
# )
# schema_view = get_schema_view(title='Pastebin API') # new


# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# NOTE : pk = course_SRS_Title
urlpatterns = [
    url("admin/test_login/", views.side_sign_in),
    path("siterequest/", views.emergency_redirect),
    path("contact/googleform/", views.googleform),
    # --------------- Helpers ------------------
    url("admin/process_requests/", views.process_requests, name="process_requests"),
    url("admin/view_requests/", views.view_requests, name="view_requests"),
    url("admin/view_canceled_SRS/", views.view_canceled_SRS),
    url("admin/delete_canceled_requests/", views.remove_canceled_requests),
    url("quickconfig/", views.quickconfig),
    # --------------- Documentation url/view -------------------
    path(
        "documentation/",
        TemplateView.as_view(template_name="documentation.html"),
        name="documentation",
    ),
    path(
        "userlookup/",
        TemplateView.as_view(template_name="admin/user_lookup.html"),
        name="user_lookup",
    ),
    url("courselookup/", views.openDataProxy),
    url(r"^api/", include(router.urls)),
    url(r"^api_doc/", schema_view),
    # --------------- Course list/detail view -------------------
    path(
        "courses/",
        views.CourseViewSet.as_view(
            {"get": "list"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-course-list",
    ),
    path(
        "courses/<course_code>/",
        views.CourseViewSet.as_view(
            {"get": "retrieve"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-course-detail",
    ),
    # --------------- Canvas Site list/detail view -------------------
    path(
        "canvassites/",
        views.CanvasSiteViewSet.as_view(
            {"get": "list"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-canvas_site-list",
    ),
    path(
        "canvassites/<canvas_id>/",
        views.CanvasSiteViewSet.as_view(
            {"get": "retrieve", "put": "update"},
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-canvas_site-detail",
    ),
    # path('courses/<int:pk>/request', views.CourseViewSet.as_view(
    #    {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
    #     name='UI-course-detail'),
    # --------------- Request list/detail view -------------------
    path(
        "requests/",
        views.RequestViewSet.as_view(
            {"get": "list", "post": "create"},
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-request-list",
    ),
    path(
        "requests/<str:pk>/",
        views.RequestViewSet.as_view(
            {"get": "retrieve", "put": "update"},
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-request-detail",
    ),
    path(
        "requests/<str:pk>/edit/",
        views.RequestViewSet.as_view(
            {"get": "retrieve"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-request-detail-edit",
    ),
    path(
        "requests/<str:pk>/success/",
        views.RequestViewSet.as_view(
            {"get": "retrieve"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-request-detail-success",
    ),
    # --------------- School list/detail view -------------------
    path(
        "schools/",
        views.SchoolViewSet.as_view(
            {
                "get": "list",
            },
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-school-list",
    ),
    path(
        "schools/<str:pk>/",
        views.SchoolViewSet.as_view(
            {"get": "retrieve", "put": "update"},
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-school-detail",
    ),
    # --------------- Subject list view -------------------
    path(
        "subjects/",
        views.SubjectViewSet.as_view(
            {"get": "list"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-subject-list",
    ),
    path(
        "subjects/<str:pk>/",
        views.SubjectViewSet.as_view(
            {"get": "retrieve", "put": "update"},
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-subject-detail",
    ),
    # --------------- AUTOADDS view -------------------
    path(
        "autoadds/",
        views.AutoAddViewSet.as_view(
            {"get": "list", "post": "create", "delete": "list"},
            renderer_classes=[renderers.TemplateHTMLRenderer],
        ),
        name="UI-autoadd-list",
    ),  # adding 'delete': 'list' is hacky but saves me from writiing a detail page in UI
    # path('users/<?:pennkey>/', UserDetail.asview(),name='user-detail'),
    # --------------- HOMEPAGE view -------------------
    path("", views.HomePage.as_view(), name="home"),
    # --------------- CONTACT view -------------------
    path("contact/", views.contact, name="contact"),
    # --------------- USERINFO view -------------------
    path("accounts/userinfo/", views.userinfo, name="userinfo"),
    # --------------- UPDATE LOG view -------------------
    path(
        "logs/",
        views.UpdateLogViewSet.as_view(
            {"get": "list"}, renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name="UI-updatelog-list",
    ),
    # --------------- Temporary Email view -------------------
    path("emails/", views.temporary_email_list, name="temporary_email"),
    path("emails/<value>/", views.my_email, name="my_email"),
    # --------------- login url/view -------------------
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            extra_context={
                "next": "/",
            },
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(
            next_page=settings.LOGOUT_REDIRECT_URL,
            template_name="logout.html",
        ),
        name="logout",
    ),
    # --------------- Canvas Proxies -------------------
    url(r"^canvasuser/(?P<username>\w+)/$", views.myproxy),
    path("searchcanvas/<search>/", views.autocompleteCanvasCourse),
    # --------------- autocomplete -------------------
    # views are defined in autocomplete.py
    url(
        r"^user-autocomplete/$",
        UserAutocomplete.as_view(),
        name="user-autocomplete",
    ),
    url(
        r"^subject-autocomplete/$",
        SubjectAutocomplete.as_view(),
        name="subject-autocomplete",
    ),
    url(
        r"^canvas_site-autocomplete/$",
        CanvasSiteAutocomplete.as_view(),
        name="canvas_site-autocomplete",
    ),
]

# urlpatterns = [path(r'^siterequest/', include(urlpatterns))]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# path('course', views.CourseViewSet.as_view({'get': 'list'})),
