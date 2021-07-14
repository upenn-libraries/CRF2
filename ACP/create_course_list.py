import os
import sys

from course.models import Course


def create_unrequested_list(term, outputfile="unrequested_courses.txt"):
    print(") Finding unrequested courses...")

    term = term[-1]
    year = term[:-1]
    courses = Course.objects.filter(
        course_term=term,
        year=year,
        requested=False,
        requested_override=False,
        primary_crosslist="",
        course_schools__visible=True,
    )

    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data/", outputfile)

    with open(file_path, "w+") as output_file:
        for course in courses:
            output_file.write(
                f"{course.srs_format_primary()}, {course.course_schools.abbreviation}\n"
            )

    print(f"- Found {len(courses)} unrequested courses.")
    print("FINISHED")


def create_unused_sis_list(
    inputfile="unrequested_courses.txt", outputfile="unused_sis_ids.txt"
):
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)

    with open(file_path, "r") as dataFile:
        for line in dataFile:
            id, school = line.replace("\n", "").split(",")

    print("FINISHED")
