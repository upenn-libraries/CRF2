from configparser import ConfigParser

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

config = ConfigParser()
config.read("config/config.ini")
domain = config.get("canvas", "prod_env")
key = config.get("canvas", "prod_key")
headers = {"Authorization": "Bearer %s" % (key)}


# Canvas API URL
API_URL = domain
# Canvas API key
API_KEY = key


# --------------- RETREIVEING FROM CANVAS ------------------


def get_user_by_sis(login_id):
    # login_id == pennkey
    # https://canvas.instructure.com/doc/api/users.html
    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    # canvas.get_user(123)
    try:
        login_id_user = canvas.get_user(login_id, "sis_login_id")
        # print(login_id_user, login_id_user.attributes)
        # print(login_id_user.get_courses()[0].attributes)
        return login_id_user
    except CanvasException as e:
        print("CanvasException: ", e)
        return None


# need to test this
def mycreate_user(pennkey, pennid, email, fullname):
    # 1. create account with SIS_ID speciified
    # canvas = Canvas(API_URL, API_KEY)
    pseudonym = {"sis_user_id": pennid, "unique_id": pennkey}
    try:
        account = find_account(96678)
        user = account.create_user(pseudonym, user={"name": fullname})
        user.edit(user={"email": email})
        return user
    except CanvasException as e:
        print("CanvasException: ", e)
        return None


def get_user_courses(login_id):
    user = get_user_by_sis(login_id)
    if user is None:
        return None
    return user.get_courses(enrollment_type="teacher")


def find_in_canvas(sis_section_id):
    """
    :param sis_section_id: the SIS ID of a course. 'SRS_BIOL-101-601 2014C
    :type sis_section_id: str
    """
    # to see if the course exits just search the section
    # https://canvas.upenn.edu/api/v1/sections/sis_section_id:SRS_BIOL-101-601%202014C
    # (line 1048)
    # https://github.com/ucfopen/canvasapi/blob/49ddf3d12c411de25121a8a04b99a0b62b6a1de4/canvasapi/canvas.py

    canvas = Canvas(API_URL, API_KEY)
    try:
        section = canvas.get_section(sis_section_id, use_sis_id=True)  # , **kwargs)
    except CanvasException as e:
        print("CanvasException: ", e)
        return None
    # if bad: while(1);{"errors":[{"message":"The specified resource does not exist."}]}

    return section


def find_account(account_id):
    canvas = Canvas(API_URL, API_KEY)
    try:
        account = canvas.get_account(account_id)
        return account
    except CanvasException as e:
        print("CanvasException: ", e)
        return None


def find_term_id(account_id, sis_term_id):
    # term= 2019C
    # https://canvas.upenn.edu/api/v1/accounts/96678/terms/sis_term_id:2019C -- works
    canvas = Canvas(API_URL, API_KEY)
    account = canvas.get_account(account_id)
    if account:
        response = account._requester.request(
            "GET", "accounts/{}/terms/sis_term_id:{}".format(account_id, sis_term_id)
        )
        if response.status_code == 200:
            return response.json()["id"]
        else:
            return None
    else:
        return None


# create_course(self, **kwargs):
# course[name]
# course[sis_course_id]
# course[term_id]
# course[course_code]
# try to create something https://canvas.upenn.edu/courses/1472986


def search_course(terms):
    # https://github.com/instructure/canvas-lms/blob/master/app/controllers/search_controller.rb
    return None


# --------------- CANVAS API JSON STRUCTURE ------------------

"""
################ SECTION OBJECT ################
    {
"id": 1440128,
"course_id": 1254326,
"name": "BIOL 101-603 2014C Intro Biology A",
"start_at": null,
"end_at": null,
"created_at": "2014-08-18T21:51:30Z",
"restrict_enrollments_to_section_dates": false,
"nonxlist_course_id": null,
"sis_section_id": "SRS_BIOL-101-603 2014C",
"sis_course_id": "SRS_BIOL-101-601 2014C",
"integration_id": null,
"sis_import_id": null
}
"""


# --------------- PUTTING IN  CANVAS ------------------

"""
#######################################
########### EXAMPLE COURSE ############
#######################################
{
   'id':1448756,
   'name':'Bad Link Testing',
   'account_id':96678,
   'uuid':'TDaK94IomVMXoYKPudVwcP4YoERhhleVkTgd4PWw',
   'start_at':'2019-04-01T14:59:31Z',
   'grading_standard_id':None,
   'is_public':False,
   'created_at':'2019-04-01T14:56:39Z',
   'course_code':'zNS-BADLINK-A2019',
   'default_view':'wiki',
   'root_account_id':96678,
   'enrollment_term_id':4373,
   'license':'private',
   'end_at':None,
   'public_syllabus':False,
   'public_syllabus_to_auth':False,
   'storage_quota_mb':1000,
   'is_public_to_auth_users':False,
   'hide_final_grades':False,
   'apply_assignment_group_weights':False,
   'calendar':{
      'ics':'https://canvas.upenn.edu/feeds/calendars/course_TDaK94IomVMXoYKPudVwcP4YoERhhleVkTgd4PWw.ics'
   },
   'time_zone':'America/New_York',
   'blueprint':False,
   'sis_course_id':'zNS-BADLINK-A2019',
   'sis_import_id':None,
   'integration_id':None,
   'enrollments':[
      {
         'type':'student',
         'role':'StudentEnrollment',
         'role_id':2022,
         'user_id':5443278,
         'enrollment_state':'active'
      }
   ],
   'workflow_state':'available',
   'restrict_enrollments_to_course_dates':False
}
"""
