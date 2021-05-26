from configparser import ConfigParser

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from course.models import School

## FINISH THIS


class Command(BaseCommand):
    help = "Emergency Start Up"

    def add_arguments(self, parser):
        parser.add_argument(
            "-nr", "--norequests", action="store_true", help="ignore adding requests"
        )

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        prefix = kwargs["prefix"]
        admin = kwargs["admin"]
        courseware = kwargs["courseware"]

        for i in range(total):
            if prefix:
                username = "{prefix}_{random_string}".format(
                    prefix=prefix, random_string=get_random_string()
                )
            else:
                username = get_random_string()

            if admin:
                User.objects.create_superuser(
                    username=username, email="", password="123"
                )
            elif courseware:

                for (key, value) in config.items("users"):
                    try:
                        User.objects.create_superuser(
                            username=key, email="", password=value
                        )
                    except:
                        print("didnt add user " + key)
            else:
                User.objects.create_user(username=username, email="", password="123")
