from django.apps import AppConfig
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from .signals import request_cleanup


class CourseAppConfig(AppConfig):
    name = "course"
    # verbose_name = "Course Request Form"

    # not in use
    def ready(self):
        import course.signals  # noqa
