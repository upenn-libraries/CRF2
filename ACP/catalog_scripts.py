import datetime
import os
import sys
from configparser import ConfigParser
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException


config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas_catalog", "prod_env")  #'prod_env')
API_KEY = config.get("canvas_catalog", "prod_key")  #'prod_key')

# /view?include_new_entries=1&include_enrollment_state=1


# https://upenn-catalog.instructure.com/api/v1/courses/551/discussion_topics

# https://upenn-catalog.instructure.com/courses/551/discussion_topics


def archive_discussion(course_id):
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(course_id)
    discussions = course.get_discussion_topics()
    for discussion in discussions:
        # create file name
        outputfile = discussion.title.replace(" ", "") + ".csv"
        outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
        entries = discussion.get_topic_entries()
        for entry in entries:
            # link =
            # print(user, discussion.title)
            post = entry.message.replace("\n", "")
            user = entry.user["display_name"]
            created = entry.created_at
            print(user, discussion.title)
            outFile.write("%s|%s|%s\n" % (user, created, post))
