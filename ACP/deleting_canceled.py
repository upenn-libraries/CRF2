import datetime
import os
import sys
from configparser import ConfigParser

import requests
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from dateutil import tz

from course.models import *
from datawarehouse import datawarehouse
from datawarehouse.helpers import *

from .logger import canvas_logger, crf_logger

config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")  #'prod_env')
API_KEY = config.get("canvas", "prod_key")  #'prod_key')


def code_to_sis(course_code):
    middle = course_code[:-5][-6:]
    sis_id = "SRS_%s-%s-%s %s" % (
        course_code[:-11],
        middle[:3],
        middle[3:],
        course_code[-5:],
    )
    return sis_id


def find_delete_courses(inputfile="deletelist.txt", outputfile="deletelistSTATUS.txt"):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    delete = True
    for line in dataFile:
        # FIND IN CRF
        id = line.replace("\n", "")
        sis_id = code_to_sis(id)
        try:
            canvas_course = canvas.get_course(sis_id, use_sis_id=True)
            student_enrollments = canvas_course.get_enrollments(
                type="StudentEnrollment"
            )
            for s in student_enrollments:
                # print("COURSE:", s , sis_id)
                delete = False
            if delete == False:
                outFile.write("course, %s, activte\n" % sis_id)
            else:
                outFile.write("course, %s, inactivte\n" % sis_id)
        except:
            # lets see if it exists as a section
            try:
                section = canvas.get_section(sis_id, use_sis_id=True)
                student_enrollments = canvas_course.get_enrollments(
                    type="StudentEnrollment"
                )
                for s in student_enrollments:
                    # print("SECTION:", s , sis_id)
                    delete = False
                if delete == False:
                    outFile.write("section, %s, activte\n" % sis_id)
                else:
                    outFile.write("section, %s, inactivte\n" % sis_id)
            except:
                outFile.write("course/section, %s, missing" % sis_id)
