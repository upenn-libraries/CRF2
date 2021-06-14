# a script that generates two files 1. a .txt file of SIS IDs for courses in a
# given term that are not requested in the CRF yet 2. a .txt file of SIS IDs
# from the file in 1. but check if SIS ID in use in Canvas

import os
import sys
from configparser import ConfigParser

# from canvasapi import Canvas
# from canvasapi.exceptions import CanvasException
from course.models import Course

from .logger import canvas_logger, crf_logger

# here are most of the basic API requests that should support the CRF

config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")
API_KEY = config.get("canvas", "prod_key")


def test_log():
    canvas_logger.info("canvas test")
    crf_logger.info("crf test?!")


# def sis_id_status(id):
#     # check if sis id is in usage in Canvas
#     # returns true if SIS ID is not in use in Canvas
#     canvas = Canvas(API_URL, API_KEY)
#     try:
#         section = canvas.get_section(id, use_sis_id=True)  # , **kwargs)
#         crf_logger.info("%s already is in use" % (id))
#     except CanvasException as e:
#         print("CanvasException: ", e)
#         return False
#     return True


def create_unrequested_list(outputfile="notRequestestedSIS.txt", term="2020A"):
    # NEEDS TESTING for added column
    # creates a list of unrequested courses in the CRF based on a term
    # this list only represents the primary
    t = term[-1]
    year = term[:-1]
    c = Course.objects.filter(
        course_term=t,
        year=year,
        requested=False,
        requested_override=False,
        primary_crosslist="",
        course_schools__visible=True,
    )
    print("%d potential new course sites" % (len(c)))
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data/", outputfile)
    f = open(file_path, "w+")
    for x in c:
        f.write("%s,%s\n" % (x.srs_format_primary(), x.course_schools.abbreviation))
    print("-> Finished Generating: ", outputfile)
    print(
        "-> NEXT: Please now run `create_unused_sis_list(inputfile='%s')` to "
        "determine which of these course codes are already used in Canvas" % outputfile
    )


def create_unused_sis_list(
    inputfile="notRequestestedSIS.txt", outputfile="notUsedSIS.txt"
):
    # NEEDS TESTING for added column based on the outputfile (pass as
    # `inputfile`) from `create_unrequested_list` check that each sis id is not
    # in use in canvas.  if the sis id is NOT in use, then write to the
    # outputfile.
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    print("path", my_path)
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    print("file path", file_path)
    dataFile = open(file_path, "r")
    # notUsedSIS = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    for line in dataFile:
        id, school = line.replace("\n", "").split(",")
        # sis_id = "SRS_" + id
        # if sis_id_status(sis_id):  # returns True if sis id in use
        # canvas_logger.warning("sis_id already in use %s", sis_id)
        # else:  # sis is in use
        # notUsedSIS.write(id + "\n")

    print("-> Finished Generating: ", outputfile)
    print("-> Please Check `ACP/logs/canvas.log` for a list of SIS IDs arleady in used")
    print(
        "-> NEXT: To create Requests for these courses please run "
        "`create_requests(inputfile='%s')`" % outputfile
    )
