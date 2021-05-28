import csv
import json
import random
import re
import time
from configparser import ConfigParser

import requests

from sample_data import *

"""

  THIS FILE SERVES AS A "WRAPPER" FOR THE CRF API



Since the Django has an API endpoint data can be loaded/synced without
halting the application
see: http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/apis-without-drf.html



"""


config = ConfigParser()
config.read("../config/config.ini")


domain = config.get("django", "domain")
psswd = config.get("django", "password")
usrnm = config.get("django", "username")
auth = (usrnm, psswd)

headers = {"Content-Type": "application/json"}

########################################
### template of data in PUT requests ###
########################################
template_course_data = {}
# both are the same template
template_school_data = {"name": "", "abbreviation": "", "visible": False}


subject_data = {
    "abbreviation": "SUBJ1",
    "name": "Subj_1",
    "visible": "true",
    "schools": "school_data['abbreviation']",
}

template_user_data = {
    "username": "",
    "email": "",
    "first_name": "",
    "last_name": "",
    "penn_id": "",
}

########################################
########      Filler Data      #########
########################################

# http://www.upenn.edu/gazette/schools.html
school_data = [
    {
        "abbreviation": "AN",
        "name": "Annenberg School For Communication",
        "visibility": True,
    },
    {"abbreviation": "SAS", "name": "Arts & Sciences", "visibility": True},
    {"abbreviation": "DM", "name": "Dental Medicine", "visibility": True},
    {
        "abbreviation": "GSE",
        "name": "Graduate School Of Education",
        "visibility": False,
    },
    {"abbreviation": "SEAS", "name": "Engineering", "visibility": True},
    {"abbreviation": "FA", "name": "Design", "visibility": True},
    {"abbreviation": "LW", "name": "Law", "visibility": True},
    {"abbreviation": "PSOM", "name": "Perelman School Of Medicine", "visibility": True},
    {"abbreviation": "NURS", "name": "Nursing", "visibility": True},
    {"abbreviation": "PC", "name": "Provost Center", "visibility": True},
    {"abbreviation": "SS", "name": "Summer Sessions", "visibility": True},
    {"abbreviation": "SP2", "name": "Social Policy & Practice", "visibility": True},
    {"abbreviation": "VET", "name": "Veterinary Medicine", "visibility": True},
    {"abbreviation": "WH", "name": "Wharton", "visibility": True},
]

subject_data = [
    {"abbreviation": "abbr_1", "name": "name_1", "visibility": True},
    {"abbreviation": "abbr_2", "name": "name_2", "visibility": True},
    {"abbreviation": "abbr_3", "name": "name_3", "visibility": True},
    {"abbreviation": "abbr_4", "name": "name_4", "visibility": True},
    {"abbreviation": "abbr_5", "name": "name_5", "visibility": True},
    {"abbreviation": "abbr_6", "name": "name_6", "visibility": True},
    {"abbreviation": "abbr_7", "name": "name_7", "visibility": True},
    {"abbreviation": "abbr_8", "name": "name_8", "visibility": True},
    {"abbreviation": "abbr_9", "name": "name_9", "visibility": True},
    {"abbreviation": "abbr_10", "name": "name_10", "visibility": True},
    {"abbreviation": "abbr_11", "name": "name_11", "visibility": True},
    {"abbreviation": "abbr_12", "name": "name_12", "visibility": True},
    {"abbreviation": "abbr_13", "name": "name_13", "visibility": True},
    {"abbreviation": "abbr_14", "name": "name_14", "visibility": True},
    {"abbreviation": "abbr_15", "name": "name_15", "visibility": True},
    {"abbreviation": "abbr_16", "name": "name_16", "visibility": True},
    {"abbreviation": "abbr_17", "name": "name_17", "visibility": True},
    {"abbreviation": "abbr_18", "name": "name_18", "visibility": True},
    {"abbreviation": "abbr_19", "name": "name_19", "visibility": True},
    {"abbreviation": "abbr_20", "name": "name_20", "visibility": True},
    {"abbreviation": "abbr_21", "name": "name_21", "visibility": True},
    {"abbreviation": "abbr_22", "name": "name_22", "visibility": True},
    {"abbreviation": "abbr_23", "name": "name_23", "visibility": True},
    {"abbreviation": "abbr_24", "name": "name_24", "visibility": True},
    {"abbreviation": "abbr_25", "name": "name_25", "visibility": True},
    {"abbreviation": "abbr_26", "name": "name_26", "visibility": True},
    {"abbreviation": "abbr_27", "name": "name_27", "visibility": True},
    {"abbreviation": "abbr_28", "name": "name_28", "visibility": True},
    {"abbreviation": "abbr_29", "name": "name_29", "visibility": True},
    {"abbreviation": "abbr_30", "name": "name_30", "visibility": True},
    {"abbreviation": "abbr_31", "name": "name_31", "visibility": True},
    {"abbreviation": "abbr_32", "name": "name_32", "visibility": True},
    {"abbreviation": "abbr_33", "name": "name_33", "visibility": True},
    {"abbreviation": "abbr_34", "name": "name_34", "visibility": True},
    {"abbreviation": "abbr_35", "name": "name_35", "visibility": True},
]


user_data = [
    {"username": "username_1", "email": "email_1@gmail.com", "penn_id": "1"},
    {"username": "username_2", "email": "email_2@gmail.com", "penn_id": "2"},
    {"username": "username_3", "email": "email_3@gmail.com", "penn_id": "3"},
    {"username": "username_4", "email": "email_4@gmail.com", "penn_id": "4"},
    {"username": "username_5", "email": "email_5@gmail.com", "penn_id": "5"},
    {"username": "username_6", "email": "email_6@gmail.com", "penn_id": "6"},
    {"username": "username_7", "email": "email_7@gmail.com", "penn_id": "7"},
    {"username": "username_8", "email": "email_8@gmail.com", "penn_id": "8"},
]


# https://www.inboundnow.com/apps/kill-writers-block/
titles = [
    "What [Current Popular TV Show] Can Teach You About [Keyword]",
    "How to Recover From a [Common Problem Keyword]",
    "[Number] Crucial Tactics for [Keyword]",
    "Why Your [Keyword] is Missing the Mark (And How You Can Fix It)",
    "Back to Basics in [Keyword]",
    "[Number] Creative Ways to [Solution Keyword]",
    "[Do something] like [world-class example]",
    "Do You Recognize the [number] Early Warning Signs of [blank]?",
    "Ultimate guide to [something of popular interest]",
    "The Modern Rules of [Keyword]",
    "[Number] Reasons [Keyword] is Better Than [Alternate Keyword]"
    "How to Use [Solution Based Keyword] to [Desirable Outcome Keyword]",
]


########################################
#########  get what is in DB   #########
########################################


def get_helper(response):
    # recursively gets the next page
    try:
        link = response.links["next"]["url"]
    except KeyError:
        return []
        print("link", link)

    response = requests.get(link, headers=headers, auth=auth)
    r = response.json()
    return r + get_helper(response)


def get_instructors():
    # returns a list of users that could be an instructor
    url = domain + "users/"
    response = requests.get(url, headers=headers, auth=auth)
    print(response.status_code, url, response)
    r = response.json()
    if r == []:  # nothing here
        return None
    else:
        res = r + get_helper(response)
        # res.remove('end')
        results = [x["username"] for x in res]
        return results


def get_subjects():
    # returns a list of subjects that could be listed for a course
    url = domain + "subjects/"
    response = requests.get(url, headers=headers, auth=auth)

    r = response.json()
    if r == []:
        return None
    else:
        # print(response.links['next']) # works!
        res = r + get_helper(response)
        results = [x["abbreviation"] for x in res]
        return results


def get_schools():
    # returns a list of schools that could be listed for a course
    url = domain + "schools/"
    response = requests.get(url, headers=headers, auth=auth)
    r = response.json()
    if r == []:
        return None
    else:
        res = r + get_helper(response)
        results = [x["abbreviation"] for x in res]
        return results


def get_courses():
    # returns a list of schools that could be listed for a course
    url = domain + "courses/"
    response = requests.get(url, headers=headers, auth=auth)
    r = response.json()
    if r == []:
        return None
    else:
        res = r + get_helper(response)
        results = [x["course_code"] for x in res]
        return results


def course_is_unique(data):
    course_code = (
        data["course_primary_subject"]
        + data["course_number"]
        + data["course_section"]
        + data["year"]
        + data["course_term"]
    )
    # <subject><course_number><section><year><term>
    # self.course_code = self.course_primary_subject.abbreviation + self.course_number + self.course_section + self.year + self.course_term

    url = domain + "courses/" + course_code + "/"
    response = requests.get(url, headers=headers, auth=auth)
    print(response.status_code, url)
    if str(response.status_code)[0] == "2":
        return True
    else:
        return False


#####################################
#########  REQUEST HELPERS  #########
#####################################


def print_url(r, *args, **kwargs):
    print(r.url, r.status_code)


def record_hook(r, *args, **kwargs):
    r.hook_called = True
    return r


def check_instructor(penn_id):
    # http://127.0.0.1:8000/api/users/?profile__penn_id=8945079
    url = domain + "/users/?profile__penn_id=" + penn_id
    if str(response.status_code)[0] == "2":
        return True
    else:
        return False


def check_instance(instance, id):
    url = domain + "/" + instance + "/" + id + "/"
    response = requests.get(
        url, headers=headers, auth=auth, hooks={"response": print_url}
    )
    if str(response.status_code)[0] == "2":
        return True
    else:
        return False


####################################
#########  BASIC CREATION  #########
####################################
def create_instructor(penn_id):
    # how do i get their info??
    pass


def create_instance(uri, data):
    json_data = json.dumps(data)
    url = domain + uri + "/"
    response = requests.post(
        url, data=json_data, headers=headers, auth=auth, hooks={"response": print_url}
    )
    if str(response.status_code)[0] == "2":
        r = response.json()
        print(r)
    else:
        print(response.json())
        print("didnt create %s: \n%s" % (uri, data))


def cross_list(c1, c_list):
    # the parameters are the course_codes
    url = domain + "courses/" + c1 + "/"
    # just one crosslist
    # if c3 ==None:
    #    response = requests.patch(url, data=json.dumps({"crosslisted":[ c2]}), headers=headers,auth=auth, hooks={'response': print_url})
    # else:
    # print(c2,c3,json.dumps({"crosslisted":[c2,c3]}))
    response = requests.patch(
        url,
        data=json.dumps({"crosslisted": c_list}),
        headers=headers,
        auth=auth,
        hooks={"response": print_url},
    )


####################################
######### BULK CREATIONS ###########
####################################


def bulk_create_users():
    for usr in user_data:
        create_instance("users", usr)


def bulk_create_sub_sch():

    for school in school_data:
        create_instance("schools", school)
        number_subjects = random.randint(1, 20)
        for number in range(0, number_subjects):
            subject_data = {
                "abbreviation": school["abbreviation"] + "(" + str(number) + ")",
                "name": school["abbreviation"] + "_subj:" + str(number),
                "visible": True,
                "schools": school["abbreviation"],
            }
            print()
            create_instance("subjects", subject_data)


def bulk_crosslist():
    # goes through the pages and selects randomly
    for page in range(1, 300):
        url = domain + "courses/?page=" + str(page)
        response = requests.get(url, headers=headers, auth=auth)
        r = response.json()
        if r == []:
            return None
        else:
            res = r

            results = [x["course_code"] for x in res]
        # go thru page

        index_a = random.randrange(len(results))
        course_a = results[index_a]
        del results[index_a]
        print("course_a", course_a)
        index_b = random.randrange(len(results))
        course_b = results[index_b]
        del results[index_b]
        print("course_b", course_b)

        index_x = random.randrange(len(results))
        course_x = results[index_x]
        del results[index_x]
        index_y = random.randrange(len(results))
        course_y = results[index_y]
        del results[index_y]
        index_z = random.randrange(len(results))
        course_z = results[index_z]
        del results[index_z]

        cross_list(course_a, course_b)
        cross_list(
            course_x,
            course_y,
            course_z,
        )


def bulk_create_courses():
    # getting field possibilities
    instructors = get_instructors()
    subjects = get_subjects()
    print("ll", subjects)
    schools = get_schools()
    terms = ["A", "B", "C"]
    activity = ["LEC", "SEM", "LAB"]

    for i in range(1, 50):

        instructor_size = random.choice([1, 1, 2, 3])
        subject_size = random.choice([1, 1, 1, 1, 1, 2])
        school_size = random.choice([1, 1, 1, 2, 1])
        course_data = {
            "course_code": "x",
            "instructors": random.sample(instructors, k=instructor_size),
            "course_schools": random.sample(schools, k=school_size),
            "course_subjects": random.sample(subjects, k=subject_size),
            "course_term": random.choice(terms),
            "course_activity": random.choice(activity),
            "course_number": random.choice(["100", "200", "300"]),
            "course_section": "001",
            "course_name": random_name(),
            "year": "2019",
            "requested": False,
            "course_primary_subject": "",
        }
        if len(course_data["course_subjects"]) != 1:
            course_data["course_primary_subject"] = course_data["course_subjects"][0]
        else:
            course_data["course_primary_subject"] = course_data["course_subjects"][0]

        print("unique? ", course_is_unique(course_data))
        while course_is_unique(course_data):
            # create new data
            course_data = {
                "course_code": "x",
                "instructors": random.sample(instructors, k=instructor_size),
                "course_schools": random.sample(schools, k=school_size),
                "course_subjects": random.sample(subjects, k=subject_size),
                "course_term": random.choice(terms),
                "course_activity": random.choice(activity),
                "course_number": random.choice(["100", "200", "300"]),
                "course_section": "001",
                "course_name": random_name(),
                "year": "2019",
                "requested": False,
                "course_primary_subject": "",
            }
            if len(course_data["course_subjects"]) != 1:
                course_data["course_primary_subject"] = course_data["course_subjects"][
                    0
                ]
            else:
                course_data["course_primary_subject"] = course_data["course_subjects"][
                    0
                ]

        print("creating course")
        create_instance("courses", course_data)
        # this is just to really ensure we arent overloading anything
        time.sleep(0.1)

    # bulk_crosslist()


# update_obj()
# print("Courses\n", get_courses(),"\n" )
# print("Instructors\n", get_instructors(),"\n")
# print("Subjects\n", get_subjects(),"\n")
# print("Schools\n", get_schools(),"\n")

# print("~~~~~CREATING USERS~~~~~\n")
# print(bulk_create_users())
# print("~~~~~CREATING SCHOOLS & SUBJECTS ~~~~~\n")
# print(bulk_create_sub_sch())


# print("~~~~~CREATING COURSES ~~~~~\n")
# bulk_create_courses()

# cross_list('SRS_23','SRS_2','SRS_3')


# data = {'course_SRS_Title': 'SRS_14', 'instructors': ['username_8'], 'course_schools': ['PSOM'], 'course_subjects': ['abbr_30', 'abbr_4'], 'course_term': 'A', 'course_activity': 'Lab', 'course_name': 'course_name_14', 'requested': False}
# print(create_instance('courses',data))

"""
print("~~~~~CREATING USERS~~~~~\n")
print(bulk_create_users())
print("~~~~~CREATING SCHOOLS & SUBJECTS ~~~~~\n")
print(bulk_create_sub_sch())
get_subjects()
bulk_create_courses()
"""

"""
SEE: http://docs.python-requests.org/en/master/user/advanced/#advanced-usage


>>> verbs = requests.options('http://a-good-website.com/api/cats')
>>> print(verbs.headers['allow'])
GET,HEAD,POST,OPTIONS

"""


"""
data

<subj><course_num> <section> <year><term>
subj = 'AFRC' #swap this for crosslisted
course = '002' #swap this for crosslisted
sections = ['401','402','403','404','405','406','407']
activity = 'LEC' # well the first is lec and the rest are REC
year = '2019'
term = 'A'

"""


"""
data = {'username':'mfhodges','password':'Jessica69!'}
r = requests.post(url,json=data,headers={'Content-Type': 'application/json' })
if r.status_code != 200:
    raise ApiError('POST /api/ {}'.format(r.status_code))
token = r.json()['token']

url = 'http://127.0.0.1:8000/signs/toupdate'
headers = {'Authorization': 'Token '+token}
r = requests.get(url, headers=headers)
for item in r.json():
    url='http://127.0.0.1:8000/signs/'+str(item['id'])+'/'

    data = {'id':item['id'],'name':item['name'],'latitude':item['latitude'],
    'longitude':item['longitude'],'country':item['country'],'county':item['county'],
    'neighbourhood':item['neighbourhood'],'road':item['road'],'speedlimit':item['speedlimit'],
    'is_uploaded':True}
    r = requests.put(url,json=data,headers={'Content-Type': 'application/json',
     'Authorization': 'Token '+token})
    print(r.content)
"""
