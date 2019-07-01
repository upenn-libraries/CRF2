
from __future__ import print_function
from course.models import *
from datawarehouse.datawarehouse import *

import cx_Oracle
from configparser import ConfigParser
import logging

LOG_FILENAME ='users.log'
logging.basicConfig(filename=LOG_FILENAME,format='(%(asctime)s) %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

"""

None of these files are good yet, purely copied from last

see: https://github.com/upenn-libraries/accountservices/blob/master/accounts/models.py
about how users are added
"""


def validate_pennkey(pennkey):
    # assumes usernames are valid pennkeys
    print("validating pennkey (utils.py)")
    try:
        user = User.objects.get(username=pennkey)
    except User.DoesNotExist:
        # check if in penn db
        print("checking datawarehouse for: ", pennkey)
        userdata = datawarehouse_lookup(PPENN_KEY=pennkey)
        logging.warning(userdata)
        if userdata:
            #clean up first and last names
            first_name = userdata['firstname'].title()
            last_name = userdata['lastname'].title()
            user = User.objects.create_user(username=pennkey,first_name=first_name,last_name=last_name,email=userdata['email'])
            Profile.objects.create(user=user,penn_id=userdata['penn_id'])
        else:
            user=None
    # do a lookup in the data warehouse ?
    return user


def check_by_penn_id(PENN_ID):
    print("howdy")
    try:
        user = Profile.objects.get(penn_id=PENN_ID).user
        print("already exists")
        return user
    except:# User.DoesNotExist or Profile.DoesNotExist:
        # check if in penn db
        print("checking datawarehouse for: ", PENN_ID)
        user = datawarehouse_lookup(PPENN_ID=PENN_ID)
        if user:
            #clean up first and last names
            first_name = user['firstname'].title()
            last_name = user['lastname'].title()
            Profile.objects.create(user=User.objects.create_user(username=user['penn_key'],first_name=first_name,last_name=last_name,email=user['email']),penn_id=PENN_ID)
        else:
            print("WE HAVE A BIG PROBLEM")
            user=None
        return user



def datawarehouse_lookup(PPENN_KEY=None,PPENN_ID=None):
    ## connects to the db and makes a query
    config = ConfigParser()
    config.read('config/config.ini') # this works
    info = dict(config.items('datawarehouse'))
    #print(info)
    print("not ok",PPENN_KEY,PPENN_ID,(PPENN_ID !=None))
    connection = cx_Oracle.connect(info['user'], info['password'], info['service'])
    cursor = connection.cursor()
    if PPENN_KEY != None:
        print("looking by penn key")
        cursor.execute("""
            SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENN_ID
            FROM EMPLOYEE_GENERAL
            WHERE PENNKEY=:pennkey""",
            pennkey = PPENN_KEY)
        for fname, lname, email, pennid in cursor:
            print("Values:", [fname, lname, email, pennid])

            return {'firstname':fname, 'lastname':lname, 'email':email, 'penn_id':pennid}

    if (PPENN_ID !=None)==True:
        print("llooking by penn id")
        cursor.execute("""
            SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENN_KEY
            FROM EMPLOYEE_GENERAL
            WHERE PENN_ID=:pennid""",
            pennid = PPENN_ID)
        print(cursor)
        for fname, lname, email, penn_key in cursor:
            print("Values:", [fname, lname, email, penn_key])

            return {'firstname':fname, 'lastname':lname, 'email':email, 'penn_key':penn_key}

    #if no results
    print("no resutl?")
    return False


def find_or_create_user(pennid):
    print("checking")
    user = check_by_penn_id(pennid)
    if user: # the user exists
        print("user",user)
        return user
    else:
        return None

def check_site(sis_id,canvas_course_id):
    """
    with this function it can be verified if the course
    use the function get_course in canvas/api.py and if u get a result then you know it exists?
    """

    return None



def update_request_status():
    request_set = Request.objects.all() # should be filtered to status = approved
    print("r",request_set)
    string = ''
    if request_set:
        print("\t some requests - lets process them ")
        string = "\t some requests - dw I processed them "
        for request_obj in request_set:
            st ="\t"+request_obj.course_requested.course_code+" "+ request_obj.status
            print("ok ",st)
            # process request ( create course)

    else:
        string= "\t no requests"
        print("\t no requests")
    #print("how-do!")
    return "how-dy!"





def get_template_sites(user):
    """
    Function that determines which of a user's known course sites can
    be sourced for a Canvas content migration.
    :param request:
    :return course sites:
    """
    from siterequest.models import CourseSite, CANVAS

    pks = []
    for x in user.coursesite_set.all():
        if x.site_platform == CANVAS:
            pks.append(x.pk)
            continue
        if x.has_export:
            pks.append(x.pk)
    return CourseSite.objects.filter(pk__in=pks)
