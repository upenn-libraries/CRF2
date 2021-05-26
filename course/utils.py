from __future__ import print_function

import logging
from configparser import ConfigParser

import cx_Oracle

from canvas import api as canvas_api
from course.models import *
from datawarehouse.datawarehouse import *

LOG_FILENAME = "users.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    format="(%(asctime)s) %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

"""

None of these files are good yet, purely copied from last

see: https://github.com/upenn-libraries/accountservices/blob/master/accounts/models.py
about how users are added
"""


def validate_pennkey(pennkey):
    # assumes usernames are valid pennkeys
    if isinstance(pennkey, str):
        pennkey = pennkey.lower()
    print("validating pennkey (utils.py)", pennkey)
    try:
        user = User.objects.get(username=pennkey)
    except User.DoesNotExist:
        # check if in penn db
        print("checking datawarehouse for: ", pennkey)
        userdata = datawarehouse_lookup(PPENN_KEY=pennkey)
        logging.warning(userdata)
        if userdata:
            # clean up first and last names
            first_name = userdata["firstname"].title()
            last_name = userdata["lastname"].title()
            user = User.objects.create_user(
                username=pennkey,
                first_name=first_name,
                last_name=last_name,
                email=userdata["email"],
            )
            Profile.objects.create(user=user, penn_id=userdata["penn_id"])
        else:
            user = None
    # do a lookup in the data warehouse ?
    return user


def check_by_penn_id(PENN_ID):
    print("in check_by_penn_id ", PENN_ID)
    try:
        user = Profile.objects.get(penn_id=PENN_ID).user
        print("already exists,", user)
        return user
    except:  # User.DoesNotExist or Profile.DoesNotExist:
        # check if in penn db
        print("checking datawarehouse for: ", PENN_ID)
        lookupuser = datawarehouse_lookup(PPENN_ID=PENN_ID)
        print("we looked up user", lookupuser)
        if lookupuser:
            print("we are now creating the user", lookupuser["penn_key"])
            # clean up first and last names
            first_name = lookupuser["firstname"].title()
            last_name = lookupuser["lastname"].title()
            user = User.objects.create_user(
                username=lookupuser["penn_key"],
                first_name=first_name,
                last_name=last_name,
                email=lookupuser["email"],
            )
            Profile.objects.create(user=user, penn_id=PENN_ID)

        else:
            print("WE HAVE A BIG PROBLEM")
            user = None
        return user


def datawarehouse_lookup(PPENN_KEY=None, PPENN_ID=None):
    input_id = PPENN_ID
    ## connects to the db and makes a query
    config = ConfigParser()
    config.read("config/config.ini")  # this works
    info = dict(config.items("datawarehouse"))

    # print("not ok",PPENN_KEY,input_id,(PPENN_ID !=None))

    connection = cx_Oracle.connect(info["user"], info["password"], info["service"])
    cursor = connection.cursor()
    if PPENN_KEY:
        print("looking by penn key")
        cursor.execute(
            """
            SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENN_ID
            FROM EMPLOYEE_GENERAL
            WHERE PENNKEY = :pennkey""",
            pennkey=PPENN_KEY,
        )
        for fname, lname, email, pennid in cursor:
            print("Values:", [fname, lname, email, pennid])

            return {
                "firstname": fname,
                "lastname": lname,
                "email": email,
                "penn_id": pennid,
            }

    # FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENN_KEY
    if input_id:
        print("looking by penn id")
        cursor.execute(
            """
            SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENNKEY
            FROM EMPLOYEE_GENERAL
            WHERE PENN_ID = :pennid""",
            pennid=input_id,
        )
        print(cursor)
        for fname, lname, email, penn_key in cursor:
            print("Values:", [fname, lname, email, penn_key])

            return {
                "firstname": fname,
                "lastname": lname,
                "email": email,
                "penn_key": penn_key,
            }

    # if no results
    print("no result?")
    return False


def find_or_create_user(pennid):

    user = check_by_penn_id(pennid)
    if user:  # the user exists
        print("user", user)
        return user
    else:
        return None


def check_site(sis_id, canvas_course_id):
    """
    with this function it can be verified if the course
    use the function get_course in canvas/api.py and if u get a result then you know it exists?
    """

    return None


def update_request_status():
    request_set = Request.objects.all()  # should be filtered to status = approved
    print("r", request_set)
    string = ""
    if request_set:
        print("\t some requests - lets process them ")
        string = "\t some requests - dw I processed them "
        for request_obj in request_set:
            st = (
                "\t"
                + request_obj.course_requested.course_code
                + " "
                + request_obj.status
            )
            print("ok ", st)
            # process request ( create course)
    else:
        string = "\t no requests"
        print("\t no requests")
    # print("how-do!")
    return "how-dy!"


def get_template_sites(user):
    """
    Function that determines which of a user's known course sites can
    be sourced for a Canvas content migration.
    """
    courses = data.get_courses(enrollment_type="teacher")
    items = ["id", "name", "account_id", "sis_course_id", "start_at", "workflow_state"]
    for course in courses:
        # TO DO !
        # CHECK THAT COURSES ARE SYNCED
        print("course", course)
        other += [{k: course.attributes.get(k, "NONE") for k in items}]
    print(other)


def updateCanvasSites(pennkey):
    canvas_courses = canvas_api.get_user_courses(pennkey)
    if canvas_courses != None:
        for canvas_course in canvas_courses:
            try:
                here = CanvasSite.objects.update_or_create(
                    canvas_id=str(canvas_course.id),
                    workflow_state=canvas_course.workflow_state,
                    sis_course_id=canvas_course.sis_course_id,
                    name=canvas_course.name,
                )
                here[0].owners.add(User.objects.get(username=pennkey))
            except:
                print("couldnt add course", canvas_course.id)


def find_no_canvas_account():
    users = User.objects.all()
    for user in users:
        this_user = canvas_api.get_user_by_sis(user.username)
        if this_user == None:
            print(user.username)
            try:
                profile = user.profile
                canvas_api.mycreate_user(
                    user.username,
                    user.profile.penn_id,
                    user.email,
                    user.first_name + " " + user.last_name,
                )
            except:
                # profile doesnt exist yet
                userdata = datawarehouse_lookup(PPENN_KEY=user.username)
                if userdata:
                    Profile.objects.create(user=user, penn_id=userdata["penn_id"])
                    canvas_api.mycreate_user(
                        user.username,
                        user.profile.penn_id,
                        user.email,
                        user.first_name + " " + user.last_name,
                    )
            # input("enter to continue")


def fix_titles(roman_numeral):
    courses = Course.objects.filter(course_term="A")
    for c in courses:
        title = c.course_name
        words = title.split(" ")
        last_word = words[-1]
        if last_word == roman_numeral:
            new = last_word.upper()
            title = title.replace(last_word, new)
            c.course_name = title
            c.save()


def my_test():
    courses = Course.objects.all()
    for c in courses:
        if c.course_primary_subject != c.course_subject:
            print(c)


def crosslisting_cleanup():  # this needs to be fixed!!
    courses = (
        Course.objects.filter(requested=False)
        .exclude(primary_crosslist__isnull=True)
        .exclude(primary_crosslist__exact="")
    )
    for course in courses:
        try:
            cx = Course.objects.get(course_code=course.primary_crosslist)
            course.crosslisted.add(cx)
            course.save()
        except:
            # see if course exists if not there seeems to be an error!
            print("couldn't find course", course.primary_crosslist)


def update_sites_info(term):
    # look through all requests in a term and check the canvas sites info
    year = term[:4]
    term = term[-1]
    canvas_sites = Request.objects.filter(~Q(canvas_instance__isnull=True)).filter(
        status="COMPLETED",
        course_requested__year=year,
        course_requested__course_term=term,
    )
    for _canvas_site in canvas_sites:
        crf_canvas_site = _canvas_site.canvas_instance
        canvas = canvas_api.Canvas(canvas_api.API_URL, canvas_api.API_KEY)
        try:
            site = canvas.get_course(crf_canvas_site.canvas_id)
            # check name
            if site.name != crf_canvas_site.name:
                print((site.name, crf_canvas_site.name))
                crf_canvas_site.name = site.name
                crf_canvas_site.save()

            # check sis_course_id
            # if

            # check workflow_state
            if site.workflow_state != crf_canvas_site.workflow_state:
                print((site.workflow_state, crf_canvas_site.workflow_state))
                crf_canvas_site.workflow_state = site.workflow_state
                crf_canvas_site.save()

            # check owners

        except:
            print("couldnt find Canvas site: ", crf_canvas_site.sis_course_id)
            crf_canvas_site.workflow_state = "deleted"
            crf_canvas_site.save()
            pass  # couldnt find canvas site -- weird!!!


def process_canvas():
    users = User.objects.all()
    for user in users:
        print("adding for ", user.username)
        updateCanvasSites(user.username)
