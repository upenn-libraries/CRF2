# script that creates Requests in the CRF based on the final SIS ID file.  the
# requests are then all approved and proceed from this script also any
# additional site configurations are then implemented


# ONLY RUN THIS FROM home/crf2/ in $ python3 manage.py shell file = the 2nd file
# created in create_course_list that contains sis ids of courses that haven't
# been created yet.

import datetime
import os
import sys
from configparser import ConfigParser

from canvasapi import Canvas
from course.models import Course, Request, User
from course.tasks import create_canvas_site

from .logger import canvas_logger, crf_logger

config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")
API_KEY = config.get("canvas", "prod_key")


"""
BEFORE YOU DO ANYTHING PLEASE SYNC INSTRUCTORS AND COURSES WITH SRS!!!


Configurations to run with:

    - publish
    - enable panopto - external_tools/90311
    - copy from: 1502387
    - storage: 2GB

"""


def test_CRF_App():
    x = Course.objects.all()
    print(x[1])


def test_reading(file):
    my_path = os.path.dirname(os.path.abspath(__file__))
    print("path", my_path)
    file_path = os.path.join(my_path, "data/", file)
    print("file path", file_path)
    dataFile = open(file_path, "r")
    for line in dataFile:
        course = line.replace("\n", "")
        print("'" + course + "'")


def test_log():
    canvas_logger.info("canvas test")
    crf_logger.info("crf test?!")


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def get_FA_canvas_ids():
    reqs = [
        "ARCH2012022020C",
        "ARCH4112012020C",
        "ARCH5012012020C",
        "ARCH5012022020C",
        "ARCH5012032020C",
        "ARCH5012042020C",
        "ARCH5012052020C",
        "ARCH5012062020C",
        "ARCH5012072020C",
        "ARCH5110012020C",
        "ARCH5112012020C",
        "ARCH5112022020C",
        "ARCH5112032020C",
        "ARCH5112042020C",
        "ARCH5112052020C",
        "ARCH5211012020C",
        "ARCH5211022020C",
        "ARCH5354012020C",
        "ARCH5354022020C",
        "ARCH6012012020C",
        "ARCH6012022020C",
        "ARCH6012032020C",
        "ARCH6012042020C",
        "ARCH6012052020C",
        "ARCH6012062020C",
        "ARCH6012072020C",
        "ARCH6110012020C",
        "ARCH6110022020C",
        "ARCH6110032020C",
        "ARCH6110042020C",
        "ARCH6110052020C",
        "ARCH6110062020C",
        "ARCH6211012020C",
        "ARCH6211022020C",
        "ARCH6212202020C",
        "ARCH6310012020C",
        "ARCH6312012020C",
        "ARCH7012012020C",
        "ARCH7012022020C",
        "ARCH7012032020C",
        "ARCH7012042020C",
        "ARCH7012052020C",
        "ARCH7012062020C",
        "ARCH7012072020C",
        "ARCH7012082020C",
        "ARCH7012092020C",
        "ARCH7012102020C",
        "ARCH7012112020C",
        "ARCH7014072020C",
        "ARCH7032012020C",
        "ARCH7032022020C",
        "ARCH7032032020C",
        "ARCH7092012020C",
        "ARCH7110012020C",
        "ARCH7110032020C",
        "ARCH7110052020C",
        "ARCH7110062020C",
        "ARCH7190012020C",
        "ARCH7214012020C",
        "ARCH7240012020C",
        "ARCH7310012020C",
        "ARCH7320012020C",
        "ARCH7320022020C",
        "ARCH7320032020C",
        "ARCH7320042020C",
        "ARCH7320052020C",
        "ARCH7370012020C",
        "ARCH7390012020C",
        "ARCH7410012020C",
        "ARCH7412012020C",
        "ARCH7412022020C",
        "ARCH7430012020C",
        "ARCH7490012020C",
        "ARCH7500012020C",
        "ARCH7540012020C",
        "ARCH7650012020C",
        "ARCH8010012020C",
        "ARCH8030012020C",
        "ARCH8050012020C",
        "ARCH8070012020C",
        "ARCH8110012020C",
        "CPLN5004012020C",
        "CPLN5010012020C",
        "CPLN5010022020C",
        "CPLN5034012020C",
        "CPLN5034022020C",
        "CPLN5040012020C",
        "CPLN5090012020C",
        "CPLN5200012020C",
        "CPLN5400012020C",
        "CPLN5770012020C",
        "CPLN5910012020C",
        "CPLN6200012020C",
        "CPLN6270012020C",
        "CPLN6350012020C",
        "CPLN6520012020C",
        "CPLN6600012020C",
        "CPLN6620012020C",
        "CPLN7010012020C",
        "CPLN7030012020C",
        "CPLN7040012020C",
        "CPLN7050012020C",
        "CPLN7070012020C",
        "CPLN8000012020C",
        "DSGN2204012020C",
        "DSGN2344012020C",
        "DSGN2354012020C",
        "DSGN2354022020C",
        "DSGN2364012020C",
        "DSGN2644012020C",
        "DSGN2644022020C",
        "DSGN2644052020C",
        "DSGN2664012020C",
        "DSGN2664022020C",
        "DSGN3004012020C",
        "DSGN3064012020C",
        "DSGN3804012020C",
        "DSGN4883012020C",
        "FNAR0614012020C",
        "FNAR0614022020C",
        "FNAR0614032020C",
        "FNAR0614042020C",
        "FNAR0634012020C",
        "FNAR1234012020C",
        "FNAR1234022020C",
        "FNAR1234032020C",
        "FNAR1234052020C",
        "FNAR1244012020C",
        "FNAR1272012020C",
        "FNAR1454012020C",
        "FNAR1454022020C",
        "FNAR1464012020C",
        "FNAR2224012020C",
        "FNAR2254012020C",
        "FNAR2414012020C",
        "FNAR2504012020C",
        "FNAR2674012020C",
        "FNAR2714012020C",
        "FNAR2714022020C",
        "FNAR2714032020C",
        "FNAR2714042020C",
        "FNAR2804012020C",
        "FNAR3103012020C",
        "FNAR3344012020C",
        "FNAR3364012020C",
        "FNAR3404012020C",
        "FNAR3404022020C",
        "FNAR3404032020C",
        "FNAR3404042020C",
        "FNAR3404052020C",
        "FNAR3404062020C",
        "FNAR3404072020C",
        "FNAR3404082020C",
        "FNAR3404092020C",
        "FNAR3404102020C",
        "FNAR3404112020C",
        "FNAR3424012020C",
        "FNAR3484012020C",
        "FNAR4883012020C",
        "FNAR5014012020C",
        "FNAR7014012020C",
        "FNAR8014042020C",
        "FNAR8014072020C",
        "HSPV5210012020C",
        "HSPV5310012020C",
        "HSPV5520012020C",
        "HSPV5550012020C",
        "HSPV5720012020C",
        "HSPV6240012020C",
        "HSPV6241012020C",
        " HSPV6403012020C",
        "HSPV6603012020C",
        "HSPV7012012020C",
        "HSPV7012022020C",
        "HSPV7393012020C",
        "LARP5330022020C",
        "LARP5350012020C",
        "LARP5430032020C",
        "LARP6120012020C",
        "LARP7010012020C",
        "LARP7010022020C",
        "LARP7010032020C",
        "LARP7010042020C",
        "LARP7010052020C",
        "LARP7014012020C",
        "LARP7014022020C",
        "LARP7014032020C",
        "LARP7300012020C",
        "LARP7400012020C",
        "LARP7434012020C",
        "LARP7600012020C",
        "LARP7610012020C",
        "LARP7800012020C",
        "LARP780002020C",
        "LARP7800032020C",
        "MUSA5004012020C",
        "MUSA5084012020C",
        "MUSA5084022020C",
        "MUSA5090012020C",
        "MUSA5504012020C",
    ]
    for r in reqs:
        try:
            print(Request.objects.get(course_requested=r).canvas_instance.canvas_id)
        except:
            print("error with :", r)


def create_requests(inputfile="notUsedSIS.txt", copy_site=""):
    # copy_site is the canvas id of a Canvas site inwhich we'd like to copy
    # content from.
    owner = User.objects.get(username="mfhodges")
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    print("path", my_path)
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    print("file path", file_path)
    dataFile = open(file_path, "r")
    for line in dataFile:
        # FIND IN CRF
        id = line.replace("\n", "").replace(" ", "").replace("-", "")
        id = id.strip()
        print("found id: '", id, "'")
        course = get_or_none(Course, course_code=id)
        if course:
            # create request
            try:
                r = Request.objects.create(
                    course_requested=course,
                    copy_from_course=copy_site,
                    additional_instructions=(
                        "Created automatically, contact courseware support for info"
                    ),
                    owner=owner,
                    created=datetime.datetime.now(),
                )
                r.status = "APPROVED"  # mark request as approved
                r.save()
                # you have to save the course to update its request status !
                course.save()
                print("Created request for: %s" % line)
            except:
                print("\t Failed to create request for: %s" % line)
                # report that this was failed to be created
                crf_logger.info("Failed to create request for: %s", line)

        else:
            # LOG
            print("course not in CRF: %s" % line)
            crf_logger.info("Not in CRF : %s", line)
    print("-> Finished Creating Requests in CRF")
    print("-> Please check `ACP/logs/crf.log` for a list of failed Request creations")
    print("-> NEXT: Please now run `process_requests('%s')`" % inputfile)


def gather_request_process_notes(inputfile="notUsedSIS.txt"):
    # Gathers the `process_notes` for all processed requests
    # Creates a file of all of the process notes for each request (this can be
    # used to find who has a new account) Creates a file of canvas sites that
    # have been created.
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    print("file path", file_path)
    dataFile = open(file_path, "r")
    requestResultsFile = open(
        os.path.join(my_path, "ACP/data", "requestProcessNotes.txt"), "w+"
    )
    canvasSitesFile = open(
        os.path.join(my_path, "ACP/data", "canvasSitesFile.txt"), "w+"
    )
    for line in dataFile:
        # FIND IN CRF
        id = line.replace("\n", "").replace(" ", "").replace("-", "")
        course = get_or_none(Course, course_code=id)
        request = get_or_none(Request, course_requested=course)
        if request:  # the request exists
            # check if stuck in process -> log error
            if request.status == "COMPLETED":
                # find canvas site id and write that to a file with the SIS ID
                canvasSitesFile.write(
                    "%s,%s\n" % (id, request.canvas_instance.canvas_id)
                )
                requestResultsFile.write("%s | %s\n" % (id, request.process_notes))
            else:
                canvas_logger.info("request incomplete for %s", id)
        else:
            # no request exists? thats concerning.. lets log that
            crf_logger.info("couldnt find request for %s", id)


def process_requests(file="notUsedSIS.txt"):

    # THERE IS A BUG IN THE FOLLOWING FUNCTION THAT DOES NOT ALLOW A CREATION TO
    # FAIL SILENTLY
    create_canvas_site()  # runs the task
    # should wait till the above task is done...
    print("\t-> Finished Processing Requests in CRF")
    print(
        "\t-> NOW: gathering Request Processing Report in "
        "`ACP/data/requestProcessNotes.txt`"
    )
    gather_request_process_notes(file)
    print("-> Finished Generating: `ACP/data/requestProcessNotes.txt`")
    print("-> Please Check `ACP/logs/canvas.log` for a list of incomplete Requests")
    print("-> Please Check `ACP/logs/crf.log` for a list of errors in the CRF")
    print(
        "-> Please Check `ACP/data/requestProcessNotes.txt` for a details on "
        "each Request"
    )
    print("-> NEXT: (OPTIONAL) Please now run `config_sites` to configure these sites")


""" Pre-populate with Resources: copy content from a site that has resources for
        first time Canvas users and for async/sync online instruction. Also set
        on the homepage that this site has been created for ‘Academic Continuity
        During Disruption’. Info about the closure could also be shared.
        Storage Quota: increase the storage quota from the standard 1GB to 2GB.
        Enable LTIs: automatically configure Panopto.  Automatically publish the
        site once created.
"""


def config_sites(
    inputfile="canvasSitesFile.txt",
    capacity=2,
    publish=False,
    tool=None,
    source_site=None,
):
    if source_site:
        copy_content(inputfile, source_site)
    if tool:
        enable_lti(inputfile, tool)

    config = {}
    if capacity:
        config["storage_quota_mb"] = capacity
    if publish:
        config["event"] = "offer"
    if publish or capacity:
        canvas = Canvas(API_URL, API_KEY)
        my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        print("path", my_path)
        file_path = os.path.join(my_path, "ACP/data", inputfile)
        print("file path", file_path)
        dataFile = open(file_path, "r")  # # test6660002020A,1500426
        for line in dataFile:
            canvas_id = line.replace("\n", "").split(",")[-1]
            # check that the site exists
            try:
                course_site = canvas.get_course(canvas_id)
            except:
                canvas_logger.info(
                    "(inc. quota/publish) failed to find site %s" % canvas_id
                )
                course_site = None
            if course_site:
                print(course_site)
                course_site.update(course=config)


def copy_content(file, source_site):
    # NOT TESTING THAT THE SOURCE SITE IS VALID
    # √ TESTED
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    print("path", my_path)
    file_path = os.path.join(my_path, "ACP/data", file)
    print("file path", file_path)
    dataFile = open(file_path, "r")  # # test6660002020A,1500426
    for line in dataFile:
        canvas_id = line.replace("\n", "").split(",")[-1]
        # check that the site exists
        try:
            course_site = canvas.get_course(canvas_id)
        except:
            canvas_logger.info("(copy content) failed to find site %s" % canvas_id)
            course_site = None
        if course_site:
            print(course_site)
            # contentmigration = course_site.create_content_migration(
            #     migration_type="course_copy_importer",
            #     settings={"[source_course_id": source_site},
            # )


def publish_sites(file, capacity):
    # ? TESTED
    # CAPACITY IS IN MB NOT GB
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    print("path", my_path)
    file_path = os.path.join(my_path, "ACP/data", file)
    print("file path", file_path)
    dataFile = open(file_path, "r")  # # test6660002020A,1500426
    for line in dataFile:
        canvas_id = line.replace("\n", "").split(",")[-1]
        # check that the site exists
        try:
            course_site = canvas.get_course(canvas_id)
        except:
            canvas_logger.info("(publish) failed to find site %s" % canvas_id)
            course_site = None
        if course_site:
            print(course_site)
            course_site.update(course={"storage_quota_mb": capacity, "event": "offer"})
    pass


def enable_lti(file, tool):
    # tool = "context_external_tool_90311"
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    print("path", my_path)
    file_path = os.path.join(my_path, "ACP/data", file)
    print("file path", file_path)
    dataFile = open(file_path, "r")  # # test6660002020A,1500426
    for line in dataFile:
        canvas_id = line.replace("\n", "").strip()  # .split(",")[-1]
        # check that the site exists
        try:
            course_site = canvas.get_course(canvas_id)
        except:
            print("(enable tool) failed to find site %s" % canvas_id)
            canvas_logger.info("(enable tool) failed to find site %s" % canvas_id)
            course_site = None
        if course_site:
            print(course_site)
            tabs = course_site.get_tabs()
            for tab in tabs:
                # CONFIGURING TOOL
                if tab.id == tool:
                    print("\tfound tool")
                    try:
                        if tab.visibility != "public":
                            tab.update(hidden=False, position=3)
                            print("\t enabled tool")
                        else:
                            print("\t already enabled tool ")
                    except:
                        print("\tfailed tool %s" % canvas_id)
                else:
                    # skip this tab
                    pass
                    # course_site.update_tab( tool, {'hidden':'false','position':3})
            pass
