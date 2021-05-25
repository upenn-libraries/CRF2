# myscript.py
from __future__ import print_function
import cx_Oracle
from configparser import ConfigParser
import string
import logging
from course import utils
import re
from OpenData.library import *
from course.models import *


######
# If you want to omitt a parameter pass '*' instead.
#
#####
def search_course(subject_area, course_number="*", sect_number="*", term="*"):

    config = ConfigParser()
    config.read("config/config.ini")
    # check that term is available!
    info = dict(config.items("datawarehouse"))
    connection = cx_Oracle.connect(info["user"], info["password"], info["service"])
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
          cs.section_id
          || cs.term section,
          cs.section_id,
          cs.term,
          cs.subject_area subject_id,
          cs.tuition_school school_id,
          cs.xlist,
          cs.xlist_primary,
          cs.activity,
          cs.section_dept department,
          cs.section_division division,
          trim(cs.title) srs_title,
          cs.status srs_status,
          cs.schedule_revision
        FROM
          dwadmin.course_section cs
        WHERE
          cs.section_number= :section_number
        AND cs.subject_area= :subject_area
        AND cs.course_number= :course_number
        AND cs.term= :term""",
        term=term,
        section_number=sect_number,
        course_number=course_number,
        subject_area=subject_area,
    )

    for data in cursor:
        return data


def is_canceled(course_code):
    """
    O      The course section has space available
    C      The course section has no space available
    H      The course section is on hold, pending review by department
    X      The course section has been cancelled
    """
    middle = course_code[:-5][4:]
    # return("%s-%s-%s %s" % (coursecode[:-11], middle[:3],middle[3:], coursecode[-5:] ))
    subject = course_code[:-11]
    course_number = middle[:3]
    course_section = middle[3:]
    term = course_code[-5:]
    data = search_course(subject, course_number, course_section, term)
    if data:
        status = data[-2]
    else:
        return "ERROR"
    if status == "X":
        print("%s is canceled" % course_code)
        return True
