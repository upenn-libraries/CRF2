from configparser import ConfigParser

from django.core.management.base import BaseCommand

from course.models import School

config = ConfigParser()
config.read("config/config.ini")


opendata_crf_school_mappings = {
    "DM": "DM",
    "ED": "GSE",
    "EG": "SEAS",
    "VM": "VET",
    "AN": "AN",
    "FA": "FA",
    "AS": "SAS",
    "WH": "WH",
    "MD": "PSOM",
    "PV": "PC",
    "SW": "SP2",
    "LW": "LW",
    "NU": "NURS",
}

school_data = [
    {
        "abbreviation": "AN",
        "name": "Annenberg School For Communication",
        "visibility": True,
        "opendata_abbr": "AN",
        "canvas_subaccount": 99243,
    },
    {
        "abbreviation": "SAS",
        "name": "Arts & Sciences",
        "visibility": True,
        "opendata_abbr": "AS",
        "canvas_subaccount": 99237,
    },
    {
        "abbreviation": "DM",
        "name": "Dental Medicine",
        "visibility": True,
        "opendata_abbr": "DM",
        "canvas_subaccount": 99241,
    },
    {
        "abbreviation": "GSE",
        "name": "Graduate School Of Education",
        "visibility": False,
        "opendata_abbr": "ED",
        "canvas_subaccount": 82192,
    },
    {
        "abbreviation": "SEAS",
        "name": "Engineering",
        "visibility": True,
        "opendata_abbr": "EG",
        "canvas_subaccount": 99238,
    },
    {
        "abbreviation": "FA",
        "name": "Design",
        "visibility": True,
        "opendata_abbr": "FA",
        "canvas_subaccount": 99244,
    },
    {"abbreviation": "LW", "name": "Law", "visibility": True, "opendata_abbr": "LW"},
    {
        "abbreviation": "PSOM",
        "name": "Perelman School Of Medicine",
        "visibility": True,
        "opendata_abbr": "MD",
        "canvas_subaccount": 99242,
    },
    {
        "abbreviation": "NURS",
        "name": "Nursing",
        "visibility": True,
        "opendata_abbr": "NU",
        "canvas_subaccount": 99239,
    },
    {
        "abbreviation": "PC",
        "name": "Provost Center",
        "visibility": True,
        "opendata_abbr": "PV",
    },
    {
        "abbreviation": "SS",
        "name": "Summer Sessions",
        "visibility": True,
        "opendata_abbr": "SS",
    },
    {
        "abbreviation": "SP2",
        "name": "Social Policy & Practice",
        "visibility": True,
        "opendata_abbr": "SW",
        "canvas_subaccount": 99240,
    },
    {
        "abbreviation": "VET",
        "name": "Veterinary Medicine",
        "visibility": True,
        "opendata_abbr": "VM",
        "canvas_subaccount": 132153,
    },
    {
        "abbreviation": "WH",
        "name": "Wharton",
        "visibility": True,
        "opendata_abbr": "WH",
        "canvas_subaccount": 81471,
    },
]


class Command(BaseCommand):
    help = "Add schools (see file for data)"

    def handle(self, *args, **kwargs):
        """
        FROM MODELS
        name = models.CharField(max_length=50,unique=True)
        abbreviation = models.CharField(max_length=10,unique=True,primary_key=True)
        visible = models.BooleanField(default=True)
        opendata_abbr = models.CharField(max_length=2)
        canvas_subaccount = models.IntegerField(null=True)
        """

        print(") Adding schools...")

        for index, school in enumerate(school_data):
            message = f"- ({index + 1}/{len(school_data)})"

            try:
                if school.get("canvas_subaccount"):
                    course, created = School.objects.update_or_create(
                        name=school["name"],
                        abbreviation=school["abbreviation"],
                        defaults={
                            "visible": school["visibility"],
                            "opendata_abbr": school["opendata_abbr"],
                            "canvas_subaccount": school["canvas_subaccount"],
                        },
                    )
                else:
                    course, created = School.objects.update_or_create(
                        name=school["name"],
                        abbreviation=school["abbreviation"],
                        defaults={
                            "visible": school["visibility"],
                            "opendata_abbr": school["opendata_abbr"],
                        },
                    )

                if created:
                    print(f"{message} Added {school['name']}.")
                else:
                    print(f"{message} Updated {school['name']}.")
            except Exception as error:
                print(f"{message} - ERROR: {error}")

        print("FINISHED")
