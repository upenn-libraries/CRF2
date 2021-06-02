from configparser import ConfigParser

from django.core.management.base import BaseCommand

from course.models import Activity
from OpenData.library import OpenData

config = ConfigParser()
config.read("config/config.ini")


"""
ACTIVITY_CHOICES = (
    ('LEC', 'Lecture'),
    ('SEM', 'Seminar'),
    ('LAB', 'Laboratory'),
    ('CLN', 'Clinic'),
    ('IND', 'Independent Study'),
    ('ONL', 'Online Course'),
    ('PRC', 'SCUE Preceptorial'),
    ('PRO', 'NSO Proseminar'),
    ('REC', 'Recitation'),
    ('SEM', 'Seminar'),
    ('SRT', 'Senior Thesis'),
    ('STU', 'Studio'),
    ('MST', 'Masters Thesis'),
    ('UNK','Unknown')
)


Activity MODEL
name = models.CharField(max_length=40)
abbr = models.CharField(max_length=3, unique=True)
"""

# https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search_parameters/


class Command(BaseCommand):
    help = "Create random users"

    def add_arguments(self, parser):

        parser.add_argument(
            "-d", "--opendata", action="store_true", help="pull from OpenData API"
        )
        parser.add_argument(
            "-l", "--localstore", action="store_true", help="pull from Local Store"
        )

    def handle(self, *args, **kwargs):
        opendata = kwargs["opendata"]

        if opendata:
            domain = config.get("opendata", "domain")
            id = config.get("opendata", "id")
            key = config.get("opendata", "key")
            print(domain, id, key)
            OData = OpenData(base_url=domain, id=id, key=key)
            activities = OData.get_available_activity()
            print(activities)
            for abbr, name in activities.items():
                try:
                    print("name,abbr", name, abbr)
                    Activity.objects.create(name=name, abbr=abbr)
                except:
                    print("didnt make activity")

            # if no results
            return False
