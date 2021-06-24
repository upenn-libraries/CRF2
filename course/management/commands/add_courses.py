import json
import logging
from configparser import ConfigParser

from course.models import Activity, Course, School, Subject, User
from django.core.management.base import BaseCommand
from OpenData.library import OpenData

config = ConfigParser()
config.read("config/config.ini")


class Command(BaseCommand):
    help = "add courses"

    """
    FROM MODELS
        course_term = models.CharField(
            max_length=1,choices = TERM_CHOICES,) # self.course_term would ==
            self.SPRING || self.FALL || self.SUMMER
        course_activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
        course_code = models.CharField(max_length=150,unique=True,
            primary_key=True, editable=False)
        course_subject =
            models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='courses')
        course_primary_subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
        course_schools = models.ManyToManyField(School,related_name='courses')
        course_number = models.CharField(max_length=4, blank=False)
        course_section = models.CharField(max_length=4,blank=False)
        course_name = models.CharField(max_length=250)
        year = models.CharField(max_length=4,blank=False)
        crosslisted = models.ManyToManyField("self", blank=True,
            symmetrical=True, default=None)
        requested =  models.BooleanField(default=False)# False -> not requested
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-t", "--term", type=str, help="Define a term ( e.g. 2019A )"
        )
        parser.add_argument(
            "-o", "--opendata", action="store_true", help="pull from OpenData API"
        )
        parser.add_argument(
            "-l", "--localstore", action="store_true", help="pull from Local Store"
        )

    def handle(self, *args, **kwargs):
        print(") Adding courses...")

        opendata = kwargs["opendata"]
        year_term = kwargs["term"]
        year = year_term[:-1]
        term = year_term[-1]

        if opendata:
            domain = config.get("opendata", "domain")
            open_data_id = config.get("opendata", "id")
            key = config.get("opendata", "key")
            open_data_connection = OpenData(base_url=domain, id=open_data_id, key=key)

            data = open_data_connection.get_courses_by_term(year_term)
            page = 1

            while data is not None:
                print(f"PAGE {page}")

                if data == "ERROR":
                    print("ERROR")
                    return

                if isinstance(data, dict):
                    data = [data]

                for datum in data:
                    datum["section_id"] = datum["section_id"].replace(" ", "")
                    datum["crosslist_primary"] = datum["crosslist_primary"].replace(
                        " ", ""
                    )
                    print(f"- Adding {datum['section_id']}...")

                    try:
                        subject = Subject.objects.get(
                            abbreviation=datum["course_department"]
                        )
                    except Exception:
                        try:
                            school_code = open_data_connection.find_school_by_subj(
                                datum["course_department"]
                            )
                            school = School.objects.get(opendata_abbr=school_code)
                            subject = Subject.objects.create(
                                abbreviation=datum["course_department"],
                                name=datum["department_description"],
                                schools=school,
                            )
                        except Exception as error:
                            message = (
                                "Failed to find and create subject"
                                f" {datum['course_department']}"
                            )
                            logging.getLogger("error_logger").error(message)
                            print(f"- ERROR: {message} ({error})")

                    if datum["crosslist_primary"]:
                        primary_subject = datum["crosslist_primary"][:-6]

                        try:
                            primary_subject = Subject.objects.get(
                                abbreviation=primary_subject
                            )
                        except Exception:
                            try:
                                school_code = open_data_connection.find_school_by_subj(
                                    primary_subject
                                )
                                school = School.objects.get(opendata_abbr=school_code)
                                primary_subject = Subject.objects.create(
                                    abbreviation=primary_subject,
                                    name=datum["department_description"],
                                    schools=school,
                                )
                            except Exception as error:
                                message = (
                                    "Failed to find and create primary subject"
                                    f" {datum['course_department']}"
                                )
                                logging.getLogger("error_logger").error(message)
                                print(f"- ERROR: {message} ({error})")

                    else:
                        primary_subject = subject

                    school = primary_subject.schools

                    try:
                        activity = Activity.objects.get(abbr=datum["activity"])
                    except Exception:
                        try:
                            activity = Activity.objects.create(
                                abbr=datum["activity"], name=datum["activity"]
                            )
                        except Exception as error:
                            message = f"Failed to find activity {datum['activity']}"
                            logging.getLogger("error_logger").error(message)
                            print(f"- ERROR: {message} ({error})")

                    try:
                        course_created = Course.objects.update_or_create(
                            course_code=f"{datum['section_id']}{year_term}",
                            defaults={
                                "owner": User.objects.get(username="benrosen"),
                                "course_term": term,
                                "course_activity": activity,
                                "course_subject": subject,
                                "course_primary_subject": primary_subject,
                                "primary_crosslist": datum["crosslist_primary"],
                                "course_schools": school,
                                "course_number": datum["course_number"],
                                "course_section": datum["section_number"],
                                "course_name": datum["course_title"],
                                "year": year,
                            },
                        )

                        course, created = course_created

                        if created:
                            print("\t* Course CREATED")
                        else:
                            print("\t* Course UPDATED")

                        if datum["is_cancelled"]:
                            course.delete()
                    except Exception as error:
                        logging.getLogger("error_logger").error(error)
                        print(f"- ERROR:{error}")

                page += 1
                data = open_data_connection.next_page()

            print("FINISHED")
        else:
            with open("OpenData/OpenData.json") as json_file:
                data = json.load(json_file)

                for school, subjects in data["school_subj_map"].items():
                    try:
                        this_school = School.objects.get(opendata_abbr=school)
                    except Exception as error:
                        print(f"- ERROR: {error}")

                    for subject in subjects:
                        if not Subject.objects.filter(abbreviation=subject).exists():
                            try:
                                subject_name = data["departments"][subject]
                                Subject.objects.create(
                                    name=subject_name,
                                    abbreviation=subject,
                                    visible=True,
                                    schools=this_school,
                                )
                            except Exception:
                                Subject.objects.create(
                                    name=subject + "-- FIX ME",
                                    abbreviation=subject,
                                    visible=True,
                                    schools=this_school,
                                )
