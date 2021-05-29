import datetime
import os
import sys
from configparser import ConfigParser

from canvasapi import Canvas
from course.models import CanvasSite, Course, Request, User
from datawarehouse.helpers import is_canceled
from dateutil import tz

config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")
API_KEY = config.get("canvas", "prod_key")

headers = {
    "Authorization": "Bearer " + API_KEY,
}


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def get_user_by_sis(login_id):
    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    # canvas.get_user(123)
    try:
        login_id_user = canvas.get_user(login_id, "sis_login_id")
        return login_id_user
    except:
        # print("CanvasException: ", e)
        return None


def enroll_instructors(sis_id, instructors):
    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    canvas_course = canvas.get_course(sis_id)
    section = canvas_course.get_sections()[0]
    for instructor in instructors:
        user = get_user_by_sis(instructor)
        if user:
            canvas_course.enroll_user(
                user.id,
                "TeacherEnrollment",
                enrollment={
                    "enrollment_state": "active",
                    "course_section_id": section.id,
                },
            )
        else:
            print("cant find %s" % instructor)
    print(canvas_course)


def canvastime_to_datetime(time_str):
    """
    datetime.datetime() is a combination of a date and a time.
    Attributes: year, month, day, hour, minute, second, microsecond, and tzinfo.
    >>> datetime.datetime.now()
        datetime.datetime(2020, 3, 10, 23, 35, 43, 287981)
    canvas_site.created_at = '2020-01-09T19:21:22Z'
    """
    # tz = 287981 # not sure about this
    date, time = time_str.split("T")
    time = time.replace("Z", "")

    year, month, day = date.split("-")
    hour, minute, second = time.split(":")
    microsecond = 0
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        int(microsecond),
    ).replace(tzinfo=tz.UTC)


# def create_instructor_updates(yearterm):
#     term = yearterm[-1]
#     year = yearterm[:-1]
#     requests = Request.objects.filter(
#         course_requested__course_term=term, course_requested__year=year
#     )
# my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
# file_path = os.path.join(my_path, "ACP/data/", outputfile)
# f = open(file_path, "w+")
# for r in requests:
#     course = r.course_requested

# pass


def unpublish_sites(
    inputfile="canvasSitesFile.txt", outputfile="unpublishedResults.txt"
):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    for line in dataFile:
        line = line.replace("\n", "")
        course_code, canvas_id = line.split(",")
        try:
            canvas_course = canvas.get_course(canvas_id)
        except:
            outFile.write("%s, could not find" % course_code)
            canvas_course = None

        if canvas_course:
            canvas_course.update(course={"event": "claim"})
            outFile.write("%s, unpublished" % course_code)


def check_crf_canceled(yearterm, outputfile="checkingCanceled.txt"):
    term = yearterm[-1]
    year = yearterm[:-1]
    requests = Request.objects.filter(
        course_requested__course_term=term, course_requested__year=year
    )
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data/", outputfile)
    f = open(file_path, "w+")
    for r in requests:
        course = r.course_requested
        is_cancel = is_canceled(course.course_code)
        if is_cancel:
            f.write("CANCELED:%s\n" % course.course_code)
        if is_cancel == "ERROR":
            f.write("ERROR:%s\n" % course.course_code)


def check_file_canceled(
    inputfile="checkingCanceled.txt",
    outputfile="confirmedCanceled.txt",
    use_sis_id=False,
):
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    for line in dataFile:
        # FIND IN CRF
        id = line.replace("\n", "").replace("ERROR:", "").replace("CANCELED:", "")
        try:
            is_canceled_status = is_canceled(id, use_sis_id)
        except:
            is_canceled_status = None
        if is_canceled_status:
            outFile.write("CANCELED,%s\n" % id)
        else:
            outFile.write("OPEN,%s\n" % id)

        # def recreate_deleted_requests(inputfile="checkingCanceled.txt"):
        #     """
        #     recreate requests that were accidentally deleted and set a message
        #     about it
        #     """
        # canvas = Canvas(API_URL, API_KEY)
        # my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        # file_path = os.path.join(my_path, "ACP/data", inputfile)
        # dataFile = open(file_path, "r")
        # for line in dataFile:
        id = line.replace("\n", "").replace("ERROR:", "").replace("CANCELED:", "")
        # crf_course = get_or_none(Course, course_code=id)
        # sis_id = "SRS_" + crf_course.srs_format()
        # canvas_crf_obj = get_or_none(CanvasSite, sis_course_id=sis_id)
        # canvas_site = canvas.get_course(sis_id, use_sis_id=True)
        # if crf_course and canvas_crf_obj and canvas_site:
        #     r = Request.objects.create(
        #         course_requested=course,
        #         copy_from_course=copy_site,
        #         additional_instructions="Accidentally deleted and recreated
        #         for archiving, contact courseware support for info",
        #         owner=owner,
        #         created=datetime.datetime.now(),
        #         status="COMPLETED",
        #     )
        # else:
        #     #
        #     pass


def update_accidentally_deleted_crf(
    yearterm, outputfile="update_accidentally_deleted_crf.txt"
):
    """ """
    owner = User.objects.get(username="mfhodges")
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", outputfile)
    dataFile = open(file_path, "w+")
    r = None
    term = yearterm[-1]
    year = yearterm[:-1]
    canvas = Canvas(API_URL, API_KEY)
    # EDIT THIS FOLLOWING LINE AS U NEED!
    courses = Course.objects.filter(
        course_term=term,
        year=year,
        requested=False,
        course_schools__visible=True,
        primary_crosslist="",
    )
    count = courses.count()
    counter = 1
    for course in courses:
        print("%s/%s" % (counter, count))
        counter += 1
        # check if the sis id is in use
        sis_id = "SRS_" + course.srs_format()
        try:
            canvas_course = canvas.get_course(sis_id, use_sis_id=True)
        except:
            # no course
            dataFile.write(" no canvas course, %s\n" % sis_id)
            canvas_course = None
        if canvas_course:
            # create request if created_at begins with '2020-03-09'
            if canvas_course.created_at[:10] == "2020-03-09":
                dataFile.write("found deleted request, %s \n" % sis_id)
                crf_canvas_site = get_or_none(CanvasSite, sis_course_id=sis_id)
                if crf_canvas_site:
                    print(sis_id)
                    r = Request.objects.create(
                        course_requested=course,
                        copy_from_course="",
                        additional_instructions=(
                            "Created automatically, contact courseware support for info"
                        ),
                        owner=owner,
                        created=canvastime_to_datetime(canvas_course.created_at),
                        status="COMPLETED",
                        admin_additional_instructions=(
                            "Request accidentally deleted and recreated. See "
                            "Maddy for details"
                        ),
                        canvas_instance=crf_canvas_site,
                    )
                    course.save()
                    dataFile.write("re-created deleted request, %s \n" % sis_id)
                else:
                    dataFile.write("no canvas site on record, %s\n" % sis_id)
                    # no canvas site ??
            else:
                # course not made in provisioning
                dataFile.write("course not made in provisioning, %s\n" % sis_id)
                pass
        if r:
            other_courses = Course.objects.filter(
                primary_crosslist=course.course_code,
                course_term=term,
                year=year,
                requested=False,
                requested_override=False,
                course_schools__visible=True,
            )
            for other_course in other_courses:
                # check if requested == true n if not then update
                if other_course.requested or other_course.requested_override:
                    pass
                else:
                    # point it to the request
                    other_course.multisection_request = r
                    other_course.save()


def update_not_in_crf(yearterm):
    """ """
    term = yearterm[-1]
    year = yearterm[:-1]
    canvas = Canvas(API_URL, API_KEY)
    # EDIT THIS FOLLOWING LINE AS U NEED!
    courses = Course.objects.filter(
        course_term=term,
        year=year,
        requested_override=True,
        course_schools__visible=True,
        primary_crosslist="",
    )
    for course in courses:
        # check if the sis id is in use
        sis_id = "SRS_" + course.srs_format()
        try:
            section = canvas.get_section(sis_id, use_sis_id=True)
        except:
            # no section
            print(" no canvas section for %s" % sis_id)
            section = None
        if section:
            course.requested_override = True
            course.save()
        other_courses = Course.objects.filter(
            primary_crosslist=course.course_code,
            course_term=term,
            year=year,
            requested=False,
            requested_override=False,
            course_schools__visible=True,
        )
        for other_course in other_courses:
            other_course.requested_override = True
            other_course.save()


def check_requests(yearterm):
    """
    for a given term make sure that if a crosslisted course is requested that it
    has its secondary pointing to the request.
    """
    term = yearterm[-1]
    year = yearterm[:-1]
    courses = Course.objects.filter(
        year=year, course_term=term, primary_crosslist__isnull=False, requested=False
    )
    for course in courses:
        primary_cx = get_or_none(Course, course_code=course.primary_crosslist)
        if primary_cx:
            try:
                primary_req = primary_cx.request
            except:
                # no request???
                print("no request found for primary course %s" % primary_cx.course_code)
                primary_req = None
            if primary_req:
                course.crosslisted_request = primary_req
                course.save()


def delete_canceled(
    inputfile="checkingCanceled.txt", outputfile="deletingCanceled.txt"
):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    for line in dataFile:
        # FIND IN CRF
        id = line.replace("\n", "").replace("ERROR:", "").replace("CANCELED:", "")
        crf_course = get_or_none(Course, course_code=id)
        sis_id = "SRS_" + crf_course.srs_format()
        canvas_course = canvas.get_course(sis_id, use_sis_id=True)
        try:
            canvas_course.conclude()
            outFile.write("deleted %s canvas site\n" % sis_id)
        except:
            print("didnt delete %s site" % sis_id)
        try:
            crf_course.delete()
            outFile.write("deleted %s request\n" % sis_id)
        except:
            print("didnt delete %s request" % sis_id)


def undodelete_canceled(inputfile="crying.txt"):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    # outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    for line in dataFile:
        # FIND IN CRF
        id = line.replace("\n", "").replace("ERROR:", "").replace("CANCELED:", "")
        middle = id[:-5][-6:]
        sis_id = "SRS_%s-%s-%s %s" % (id[:-11], middle[:3], middle[3:], id[-5:])
        try:
            canvas_course = canvas.get_course(sis_id, use_sis_id=True)
        except:
            print("%s couldnt find site" % sis_id)
        try:
            status = canvas_course.workflow_state
            if status == "completed":
                print(canvas_course)
            # canvas_course.update(course={'event':'offer'})
            # print("%s offered " % sis_id)
            # print(canvas_course)
        except:
            print("%s bad" % sis_id)


def reactivate_canceled(inputfile="crying.txt"):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    # outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    counter = 1
    for line in dataFile:
        print(counter)
        counter += 1
        # FIND IN CRF
        id = line.replace("\n", "").replace("ERROR:", "").replace("CANCELED:", "")
        middle = id[:-5][-6:]
        sis_id = "SRS_%s-%s-%s %s" % (id[:-11], middle[:3], middle[3:], id[-5:])
        try:
            canvas_course = canvas.get_course(sis_id, use_sis_id=True)
            enrolls = canvas_course.get_enrollments(state="completed")
            for e in enrolls:
                try:
                    # e.deactivate("inactivate")
                    e.deactivate("inactivate")
                    e.reactivate()
                except:
                    print("failed %s" % e.id)
                    # PUT /api/v1/courses/:course_id/enrollments/:id/reactivate
                    # response =
                    # requests.post("https://canvas.upenn.edu/api/v1/courses/1494344/enrollments/%s/reactivate"
                    # % e.id

        except:
            print("%s error" % sis_id)


def reenroll_completed(sis_id):
    canvas = Canvas(API_URL, API_KEY)
    canvas_course = canvas.get_course(sis_id, use_sis_id=True)
    section = canvas_course.get_sections()[0]
    enrolls = section.get_enrollments(state="completed")
    for e in enrolls:
        try:
            e.deactivate("inactivate")
            e.reactivate()
        except:
            print(e)
