import datetime
import os
import sys
from configparser import ConfigParser
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException


config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")  #'prod_env')
API_KEY = config.get("canvas", "prod_key")  #'prod_key')


########### HELPERS ################
def code_to_sis(course_code):
    middle = course_code[:-5][-6:]
    sis_id = "SRS_%s-%s-%s %s" % (
        course_code[:-11],
        middle[:3],
        middle[3:],
        course_code[-5:],
    )
    return sis_id


####################################

# course.create_group_category()
# https://canvas.instructure.com/doc/api/group_categories.html#method.group_categories.create

# course.get_group_categories()
# https://canvas.instructure.com/doc/api/group_categories.html#method.group_categories.index

# course.get_groups()
# https://canvas.instructure.com/doc/api/groups.html#method.groups.context_index

# group_category.create_group()
# https://canvas.instructure.com/doc/api/groups.html#method.groups.create


# group.invite(invitees)
# invitees is a list of integers (user ids)
# https://canvas.instructure.com/doc/api/groups.html#method.groups.invite


# group.create_membership( user) ### USE THIS !
# param user: The object or ID of the user

# canvas = Canvas(API_URL, API_KEY)

# .create_membership(263561)


# login_id_user = canvas.get_user(pennkey, 'sis_login_id')


def find_group_in_set(groups, name):
    group_obj = None
    for group in groups:
        if group.name == name:
            group_obj = group
    return group_obj


def create_group_enrollments(
    inputfile="groups.csv", outputfile="NSO_group_enrollments.csv"
):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s, %s, %s, %s, %s \n"
        % ("canvas_course_id", "group_set", "group", "pennkey", "status")
    )
    for line in dataFile:
        course_id, groupset_name, group_name, pennkey = line.replace("\n", "").split(
            ","
        )

        canvas_site = canvas.get_course(course_id)
        # (1) check if groupset exists, if not create
        try:
            group_set = find_group_in_set(
                canvas_site.get_group_categories(), groupset_name
            )
            if group_set is None:
                raise TypeError

        except:  # create groupset
            print("creating group set: ", groupset_name)
            group_set = canvas_site.create_group_category(groupset_name)

        # (2) check if group exists, if not create
        try:
            group = find_group_in_set(group_set.get_groups(), group_name)
            if group is None:
                raise TypeError

        except:  # create group
            print("creating group: ", group_name)
            group = group_set.create_group(name=group_name)

        try:
            # (3) enroll user
            user = canvas.get_user(pennkey, "sis_login_id")
            group.create_membership(user)
            print(course_id, groupset_name, group_name, pennkey, "accepted")
            outFile.write(
                "%s, %s, %s, %s, %s \n"
                % (course_id, groupset_name, group_name, pennkey, "accepted")
            )
        except:  # membership creation failed
            print(course_id, groupset_name, group_name, pennkey, "failed")
            outFile.write(
                "%s, %s, %s, %s, %s \n"
                % (course_id, groupset_name, group_name, pennkey, "failed")
            )
