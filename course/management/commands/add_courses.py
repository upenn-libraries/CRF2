import json
import logging
import sys
from configparser import ConfigParser

from course.models import Activity, Course, School, Subject, User
from course.utils import find_or_create_user
from django.core.management.base import BaseCommand
from OpenData.library import OpenData

config = ConfigParser()
config.read("config/config.ini")


"""
from course.models import *
Course.objects.all().delete()
"""


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
            print(domain, open_data_id, key)
            open_data_connection = OpenData(base_url=domain, id=open_data_id, key=key)

            data = open_data_connection.get_courses_by_term(year_term)
            print("data", data)
            page = 1

            while data is not None:

                print("\n\tSTARTING PAGE : ", page, "\n")
                if data == "ERROR":
                    print("ERROR")
                    sys.exit()

                if isinstance(data, dict):
                    data = [data]

                for datum in data:
                    datum["section_id"] = datum["section_id"].replace(" ", "")
                    datum["crosslist_primary"] = datum["crosslist_primary"].replace(
                        " ", ""
                    )
                    print("adding ", datum["section_id"])
                    try:
                        subject = Subject.objects.get(
                            abbreviation=datum["course_department"]
                        )
                    except Exception:
                        logging.getLogger("error_logger").error(
                            "couldnt find subject %s ", datum["course_department"]
                        )
                        print("trouble finding subject: ", datum["course_department"])
                        school_code = open_data_connection.find_school_by_subj(
                            datum["course_department"]
                        )
                        school = School.objects.get(opendata_abbr=school_code)
                        subject = Subject.objects.create(
                            abbreviation=datum["course_department"],
                            name=datum["department_description"],
                            schools=school,
                        )

                    if datum["crosslist_primary"]:
                        p_subj = datum["crosslist_primary"][:-6]
                        try:
                            primary_subject = Subject.objects.get(abbreviation=p_subj)
                        except Exception:
                            logging.getLogger("error_logger").error(
                                "couldnt find subject %s ", p_subj
                            )
                            print("trouble finding primary subject: ", p_subj)
                            school_code = open_data_connection.find_school_by_subj(
                                p_subj
                            )
                            school = School.objects.get(opendata_abbr=school_code)
                            primary_subject = Subject.objects.create(
                                abbreviation=p_subj,
                                name=datum["department_description"],
                                schools=school,
                            )
                    else:
                        print(datum["crosslist_primary"], "not found")
                        primary_subject = subject

                    school = primary_subject.schools
                    try:
                        activity = Activity.objects.get(abbr=datum["activity"])
                    except Exception:
                        logging.getLogger("error_logger").error(
                            "couldnt find activity %s ", datum["activity"]
                        )
                        activity = Activity.objects.create(
                            abbr=datum["activity"], name=datum["activity"]
                        )
                    try:
                        course = Course.objects.create(
                            owner=User.objects.get(username="benrosen"),
                            course_term=term,
                            course_activity=activity,
                            course_code=datum["section_id"] + year_term,
                            course_subject=subject,
                            course_primary_subject=primary_subject,
                            primary_crosslist=datum["crosslist_primary"],
                            course_schools=school,
                            course_number=datum["course_number"],
                            course_section=datum["section_number"],
                            course_name=datum["course_title"],
                            year=year,
                        )

                        if datum["instructors"]:
                            instructors = []
                            for instructor in datum["instructors"]:
                                print("instructor", instructor)
                                try:
                                    found = find_or_create_user(instructor["penn_id"])
                                    print("found", found)
                                    if found:
                                        instructors += [found]
                                    else:
                                        print("we need to log here")
                                except Exception:
                                    print("sad")
                                    logging.getLogger("error_logger").error(
                                        "%s (%s) not found",
                                        instructor["name"],
                                        instructor["penn_id"],
                                    )
                            print("list of instructors", instructors)
                            course.instructors.set(instructors)
                            print("course instructors:", course.instructors.all())
                    except Exception as e:
                        update_course = Course.objects.filter(
                            course_code=datum["section_id"] + year_term
                        ).first()
                        if update_course:
                            print("already exists: ", datum["section_id"] + year_term)
                            if datum["is_cancelled"]:
                                update_course.delete()
                            else:
                                update_course.name = datum["course_title"]
                                if (
                                    update_course.course_primary_subject
                                    != datum["crosslist_primary"][:-6]
                                ):
                                    try:
                                        update_course.course_primary_subject = (
                                            Subject.objects.get(
                                                abbreviation=datum["crosslist_primary"][
                                                    :-6
                                                ]
                                            )
                                        )
                                    except Exception:
                                        pass
                                update_course.instructors.clear()
                                if datum["instructors"]:
                                    instructors = []
                                    for instructor in datum["instructors"]:
                                        print("instructor", instructor)
                                        try:
                                            found = find_or_create_user(
                                                instructor["penn_id"]
                                            )
                                            print("found", found)
                                            if found:
                                                instructors += [found]
                                            else:
                                                print("we need to log here")
                                        except Exception:
                                            print("sad")
                                            logging.getLogger("error_logger").error(
                                                "%s (%s) not found",
                                                instructor["name"],
                                                instructor["penn_id"],
                                            )
                                    print("list of instructors", instructors)
                                    update_course.instructors.set(instructors)
                                update_course.save()

                        else:
                            print(type(e), e.__cause__)
                            logging.getLogger("error_logger").error(
                                "couldnt add course %s ", datum["section_id"]
                            )

                page += 1
                data = open_data_connection.next_page()

        else:
            with open("OpenData/OpenData.json") as json_file:
                data = json.load(json_file)
                """
                steps
                1. iterate through school subj mapping and take each school abbr "AS"
                    a. look up "AS" as school object
                    b. iterate list of subjs
                        - look up departments['subj'] to get full name
                    c. create Subject object
                """
                for (school, subjs) in data["school_subj_map"].items():
                    print(school, subjs)
                    try:
                        this_school = School.objects.get(opendata_abbr=school)
                    except Exception:
                        print("couldnt find school " + school)

                    print(subjs)
                    for subj in subjs:
                        if not Subject.objects.filter(abbreviation=subj).exists():
                            try:
                                subj_name = data["departments"][subj]
                                Subject.objects.create(
                                    name=subj_name,
                                    abbreviation=subj,
                                    visible=True,
                                    schools=this_school,
                                )
                            except Exception:

                                print("couldnt find subj in departments: " + subj)
                                Subject.objects.create(
                                    name=subj + "-- FIX ME",
                                    abbreviation=subj,
                                    visible=True,
                                    schools=this_school,
                                )
                        else:
                            pass
