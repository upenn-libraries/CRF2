from configparser import ConfigParser

import cx_Oracle
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from course.models import Profile

config = ConfigParser()
config.read("config/config.ini")


class Command(BaseCommand):
    help = "Create random users"

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--total",
            type=int,
            help="Indicates the number of users to be created",
        )
        parser.add_argument("-p", "--prefix", type=str, help="Define a username prefix")
        parser.add_argument(
            "-a", "--admin", action="store_true", help="Create an admin account"
        )
        parser.add_argument(
            "-c",
            "--courseware",
            action="store_true",
            help="Quick add Courseware Support team as Admins",
        )
        parser.add_argument(
            "-d",
            "--department",
            type=int,
            help=(
                "add all employees with a certian PRIMARY_DEPT_ORG code (5032 &"
                "5009 is TRL)"
            ),
        )

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        prefix = kwargs["prefix"]
        admin = kwargs["admin"]
        courseware = kwargs["courseware"]
        dept = kwargs["department"]

        if total:
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
                else:
                    User.objects.create_user(
                        username=username, email="", password="123"
                    )
        if courseware:
            config = ConfigParser()
            config.read("config/config.ini")
            for (key, value) in config.items("users"):
                try:
                    User.objects.create_superuser(
                        username=key, email="", password=value
                    )
                except:
                    print("didnt add user " + key)
        if dept:
            config = ConfigParser()
            config.read("config/config.ini")  # this works
            info = dict(config.items("datawarehouse"))
            # print(info)
            connection = cx_Oracle.connect(
                info["user"], info["password"], info["service"]
            )
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENN_ID, PENNKEY
                FROM EMPLOYEE_GENERAL
                WHERE PRIMARY_DEPT_ORG= :dept_code""",
                dept_code=dept,
            )
            for fname, lname, email, penn_id, pennkey in cursor:

                try:
                    print("added:", [fname, lname, email, penn_id, pennkey])
                    user = {
                        "firstname": fname,
                        "lastname": lname,
                        "email": email,
                        "penn_id": penn_id,
                    }
                    first_name = user["firstname"].title()
                    last_name = user["lastname"].title()
                    Profile.objects.create(
                        user=User.objects.create_user(
                            username=pennkey,
                            first_name=first_name,
                            last_name=last_name,
                            email=user["email"],
                        ),
                        penn_id=user["penn_id"],
                    )
                except:
                    print("didnt add user: ", pennkey)

            # if no results
            return False
