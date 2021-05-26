# testing Provisioning process and other tests
import os
import sys
from configparser import ConfigParser

from canvasapi import Canvas

from course.models import *

from .logger import canvas_logger, crf_logger

# here are most of the basic API requests that should support the CRF

config = ConfigParser()
config.read("config/config.ini")
domain = config.get("canvas", "prod_env")  #'prod_env')
key = config.get("canvas", "prod_key")  #'prod_key')


"""
>>> from ACP.create_course_list import *
>>> create_unused_sis_list(inputfile="test.txt",outputfile="test_out.txt")

>>> from ACP.canvas_sites import *
>>> create_requests(inputfile='test_out.txt')
"""


################# OTHER  #################


def test_reading(file):
    dataFile = open(file, "r")
    for line in dataFile:
        course = line.replace("\n", "")
        print("'" + course + "'")


def test_log():
    canvas_logger.info("canvas test")
    crf_logger.info("crf test?!")


############ CREATING TEST DATA ############


def create_test_courses(section_number):
    school = School.objects.get(abbreviation="TS")
    subj = Subject.objects.get(abbreviation="test")
    activity = Activity.objects.get(abbr="LEC")
    owner = User.objects.get(username="mfhodges")
    term = "A"
    year = "2020"
    number = "666"
    name = "Test Provisioning"
    for i in range(0, section_number):
        if i >= 100:
            section = str(i)
        elif i >= 10:
            section = "0" + str(i)
        elif i < 10:
            section = "00" + str(i)
        else:
            raise Exception("section number not right")

        print(section)
        c = Course.objects.create(
            owner=owner,
            course_activity=activity,
            course_term=term,
            course_subject=subj,
            course_primary_subject=subj,
            course_schools=school,
            course_section=section,
            course_number=number,
            course_name=name,
            year=year,
        )
        c.instructors.add(owner)
        c.save()


def create_list(number, outputfile):
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data/", outputfile)
    f = open(file_path, "w+")
    for i in range(0, number):
        if i >= 100:
            section = str(i)
        elif i >= 10:
            section = "0" + str(i)
        elif i < 10:
            section = "00" + str(i)
        else:
            raise Exception("section number not right")
        f.write("test-666-%s 2020A\n" % section)
        print("test-666-%s 2020A" % section)


def delete_sites(section_number):
    # SRS_test-666-010 2020A
    beginning = "SRS_test-666-"
    end = " 2020A"
    for i in range(0, section_number):
        if i >= 100:
            section = str(i)
        elif i >= 10:
            section = "0" + str(i)
        elif i < 10:
            section = "00" + str(i)
        else:
            raise Exception("section number not right")

        sis_id = beginning + section + end
        # Initialize a new Canvas object
        canvas = Canvas(domain, key)
        c = canvas.get_course(course=sis_id, use_sis_id=True)
        c.delete()
        print(c)
