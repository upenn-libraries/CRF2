import datetime
import os
import sys

from canvas.api import get_canvas
from course.models import Course, Request, User
from course.tasks import create_canvas_site

from .logger import canvas_logger, crf_logger


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def create_requests(inputfile="unused_sis_ids.txt", copy_site=""):
    owner = User.objects.get(username="benrosen")
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)

    with open(file_path, "r") as dataFile:
        for line in dataFile:
            course_id = line.replace("\n", "").replace(" ", "").replace("-", "")
            course_id = course_id.strip()
            course = get_or_none(Course, course_code=course_id)

            if course:
                try:
                    request = Request.objects.create(
                        course_requested=course,
                        copy_from_course=copy_site,
                        additional_instructions=(
                            "Created automatically, contact courseware support for info"
                        ),
                        owner=owner,
                        created=datetime.datetime.now(),
                    )
                    request.status = "APPROVED"
                    request.save()
                    course.save()
                except Exception:
                    print(f"\t - ERROR: Failed to create request for: {line}")
                    crf_logger.info(f"\t - ERROR: Failed to create request for: {line}")

            else:
                print(f"course not in CRF: {line}")
                crf_logger.info(f"Not in CRF : {line}")
    print("FINISHED")


def gather_request_process_notes(inputfile="unused_sis_ids.txt"):
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)

    dataFile = open(file_path, "r")
    requestResultsFile = open(
        os.path.join(my_path, "ACP/data", "requestProcessNotes.txt"), "w+"
    )
    canvasSitesFile = open(
        os.path.join(my_path, "ACP/data", "canvasSitesFile.txt"), "w+"
    )

    for line in dataFile:
        course_id = line.replace("\n", "").replace(" ", "").replace("-", "")
        course = get_or_none(Course, course_code=course_id)
        request = get_or_none(Request, course_requested=course)

        if request:
            if request.status == "COMPLETED":
                canvasSitesFile.write(
                    f"{course_id}, {request.canvas_instance.canvas_id}\n"
                )
                requestResultsFile.write(f"{course_id} | {request.process_notes}\n")
            else:
                canvas_logger.info(f"request incomplete for {course_id}")
        else:
            crf_logger.info(f"couldnt find request for {course_id}")

    print("FINISHED")


def process_requests(input_file="unused_sis_ids.txt"):
    print(") Creating canvas sites...")

    create_canvas_site()

    print("FINISHED")
    print(") Gathering request process notes...")

    gather_request_process_notes(input_file)

    print("FINISHED")


def config_sites(
    input_file="canvas_sites.txt",
    capacity=2,
    publish=False,
    tool=None,
    source_site=None,
):
    if source_site:
        copy_content(input_file, source_site)
    if tool:
        enable_lti(input_file, tool)

    config = {}

    if capacity:
        config["storage_quota_mb"] = capacity

    if publish:
        config["event"] = "offer"

    if publish or capacity:
        canvas = get_canvas()
        my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_path = os.path.join(my_path, "ACP/data", input_file)
        with open(file_path, "r") as dataFile:
            for line in dataFile:
                canvas_id = line.replace("\n", "").split(",")[-1]

                try:
                    course_site = canvas.get_course(canvas_id)
                except Exception:
                    canvas_logger.info(
                        f"(inc. quota/publish) failed to find site {canvas_id}"
                    )
                    course_site = None

                if course_site:
                    course_site.update(course=config)


def copy_content(input_file, source_site):
    canvas = get_canvas()
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", input_file)
    with open(file_path, "r") as dataFile:
        for line in dataFile:
            canvas_id = line.replace("\n", "").split(",")[-1]

            try:
                course_site = canvas.get_course(canvas_id)
            except Exception:
                canvas_logger.info(f"(copy content) failed to find site {canvas_id}")
                course_site = None

            if course_site:
                course_site.create_content_migration(
                    migration_type="course_copy_importer",
                    settings={"[source_course_id": source_site},
                )


def publish_sites(input_file, capacity):
    canvas = get_canvas()
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", input_file)

    with open(file_path, "r") as dataFile:
        for line in dataFile:
            canvas_id = line.replace("\n", "").split(",")[-1]

            try:
                course_site = canvas.get_course(canvas_id)
            except Exception:
                canvas_logger.info(f"(publish) failed to find site {canvas_id}")
                course_site = None

            if course_site:
                course_site.update(
                    course={"storage_quota_mb": capacity, "event": "offer"}
                )


def enable_lti(input_file, tool):
    canvas = get_canvas()
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", input_file)

    with open(file_path, "r") as dataFile:
        for line in dataFile:
            canvas_id = line.replace("\n", "").strip()

            try:
                course_site = canvas.get_course(canvas_id)
            except Exception:
                print(f"(enable tool) failed to find site {canvas_id}")
                canvas_logger.info(f"(enable tool) failed to find site {canvas_id}")
                course_site = None

            if course_site:
                tabs = course_site.get_tabs()

                for tab in tabs:
                    if tab.id == tool:
                        print("\tFound tool")

                        try:
                            if tab.visibility != "public":
                                tab.update(hidden=False, position=3)
                                print("\tEnabled tool")
                            else:
                                print("\tAlready enabled tool ")
                        except Exception:
                            print(f"\tFailed tool {canvas_id}")
