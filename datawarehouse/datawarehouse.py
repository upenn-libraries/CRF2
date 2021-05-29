from __future__ import print_function

import logging
import re
import string
from configparser import ConfigParser
from datetime import datetime

import cx_Oracle
from course import utils
from course.models import *
from OpenData.library import *


def get_credentials():
    config = ConfigParser()
    config.read("config/config.ini")
    values = dict(config.items("datawarehouse"))
    return values["user"], values["password"], values["service"]


def roman_title(title):
    roman_numeral = re.findall(r" [MDCLXVI]+", title)
    title = string.capwords(title)
    if roman_numeral:
        title = title.replace(roman_numeral[-1].upper(), roman_numeral[-1][1:])
    return title


def userlookup(pennid):
    config = ConfigParser()
    config.read("config/config.ini")
    info = dict(config.items("datawarehouse"))
    connection = cx_Oracle.connect(info["user"], info["password"], info["service"])
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENNKEY
        FROM EMPLOYEE_GENERAL
        WHERE PENN_ID= :pennid """,
        pennid=str(pennid),
    )
    for fname, lname, email, pennkey in cursor:
        print("Values:", [fname, lname, email, pennkey])
        return [fname, lname, email, pennkey]


# def update_courses(term):
#     # check if the term is closed
#     pass


def pull_courses(term):
    config = ConfigParser()
    config.read("config/config.ini")
    domain = config.get("opendata", "domain")
    id = config.get("opendata", "id")
    key = config.get("opendata", "key")
    OData_lookup = OpenData(base_url=domain, id=id, key=key)

    # check that term is available
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
      cs.activity IN ('LEC', 'REC', 'LAB', 'SEM', 'CLN', 'CRT', 'PRE', 'STU', 'ONL', 'HYB')
    AND cs.tuition_school NOT IN ('WH', 'LW')
    AND cs.status in ('O')
    AND cs.term = :term""",
        term=term,
    )
    # term_varaible = str(term))

    for (
        course_code,
        section_id,
        term,
        subject_area,
        school,
        xc,
        xc_code,
        activity,
        section_dept,
        section_division,
        title,
        status,
        rev,
    ) in cursor:
        print(
            course_code,
            section_id,
            term,
            subject_area,
            school,
            xc,
            xc_code,
            activity,
            section_dept,
            section_division,
            title,
            status,
            rev,
        )

        # ('VCSP6380012019C', 'VCSP638001', '2019C', 'VCSP', 'VM', None, 'VCSP638001', 'LEC', 'VCSP', None, 'LEGAL ISSUES FOR VETS', '2019-10-28 00:00:00', '2019-12-16 00:00:00', 'O', '6')
        course_code = course_code.replace(" ", "")
        primary_crosslist = ""
        subject_area = subject_area.replace(" ", "")
        xc_code = xc_code.replace(" ", "")
        print("subject_area", subject_area)
        print("adding ", course_code)
        try:
            subject = Subject.objects.get(abbreviation=subject_area)
        except:
            logging.getLogger("error_logger").error(
                "couldnt find subject %s ", subject_area
            )
            print("trouble finding subject: ", subject_area)
            school_code = OData_lookup.find_school_by_subj(subject_area)
            if school_code:
                try:
                    school = School.objects.get(opendata_abbr=school_code)
                    # NEEDS TO GET SUBJECT AREA NAME
                    subject = Subject.objects.create(
                        abbreviation=subject_area, name=subject_area, schools=school
                    )
                except:
                    print("couldn't find school ", school_code)

        # check if this course is crosslisted with anything
        if xc:  # xc can be 'S', 'P' or None
            if xc == "S":  # this is the secondary cross listing
                primary_crosslist = xc_code + term
            else:
                primary_crosslist = ""
            p_subj = xc_code[:-6]
            try:
                primary_subject = Subject.objects.get(abbreviation=p_subj)
            except:
                logging.getLogger("error_logger").error(
                    "couldnt find subject %s ", p_subj
                )
                print("trouble finding primary subject: ", p_subj)
                school_code = OData_lookup.find_school_by_subj(p_subj)
                school = School.objects.get(opendata_abbr=school_code)
                primary_subject = Subject.objects.create(
                    abbreviation=p_subj, name=p_subj, schools=school
                )
        else:
            print("crosslist_primary", xc_code, "not found")
            primary_subject = subject

        school = primary_subject.schools
        try:
            activity = Activity.objects.get(abbr=activity)
        except:
            logging.getLogger("error_logger").error(
                "couldnt find activity %s ", activity
            )
            activity = Activity.objects.create(abbr=activity, name=activity)

        try:
            # cut off term (5), get last 6 digits ( number & section )
            n_s = course_code[:-5][-6:]
            course_number = n_s[:3]
            section_number = n_s[-3:]
            roman_numeral = re.findall(r"[MDCLXVI]+", title)
            title = string.capwords(title)
            if roman_numeral:
                title = roman_title(title)
            year = term[:4]

            course = Course.objects.create(
                owner=User.objects.get(username="mfhodges"),
                course_term=term[-1],
                course_activity=activity,
                course_code=course_code,
                course_subject=subject,
                course_primary_subject=primary_subject,
                primary_crosslist=primary_crosslist,
                course_schools=school,
                course_number=course_number,
                course_section=section_number,
                course_name=title,
                year=year,
            )
            # print({'course_term' : term,
            #'course_activity' : activity,
            #'course_code' : course_code,
            #'course_subject' : subject,
            #'course_primary_subject' : primary_subject,
            #'primary_crosslist' : primary_crosslist,
            #'course_schools' : school,
            #'course_number' : course_number,
            #'course_section' : section_number,
            #'course_name' : title,
            #'year' :year})

        except Exception as e:
            # check if updates !
            # 1. check if the course exists
            #   a. find the course
            #   b. check if the primary_crosslist and course_primary_subject needs to be updated
            #   c. update the crosslistings?
            #
            # 2. if doesnt exist -- report error
            print(
                {
                    "course_term": term,
                    "course_activity": activity,
                    "course_code": course_code,
                    "course_subject": subject,
                    "course_primary_subject": primary_subject,
                    "primary_crosslist": primary_crosslist,
                    "course_schools": school,
                    "course_number": course_number,
                    "course_section": section_number,
                    "course_name": title,
                    "year": year,
                }
            )

            print(type(e), e.__cause__)

            # course doesnt already exist
            #    print(type(e),e.__cause__)
            #    #logging.getLogger("error_logger").error("couldnt add course %s ",datum["section_id"])
    print("DONE LOADING COURSES")

    # check if it already exists


def pull_instructors(term):
    user, password, service = get_credentials()
    connection = cx_Oracle.connect(user, password, service)
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT
    e.FIRST_NAME,
    e.LAST_NAME,
    e.PENNKEY,
    e.PENN_ID,
    e.EMAIL_ADDRESS,
    cs.Section_Id
    FROM
    dwadmin.course_section_instructor cs
    JOIN DWADMIN.EMPLOYEE_GENERAL_V e ON cs.Instructor_Penn_Id=e.PENN_ID
    WHERE cs.TERM= :term""",
        term=term,
    )

    NEW_INSTRUCTOR_VALUES = dict()

    for first_name, last_name, pennkey, penn_id, email, section_id in cursor:
        course_code = (section_id + term).replace(" ", "")
        try:
            course = Course.objects.get(course_code=course_code)
            if course.requested == False:
                try:
                    instructor = User.objects.get(username=pennkey)
                except:
                    try:
                        first_name = first_name.title()
                        last_name = last_name.title()
                        instructor = User.objects.create_user(
                            username=pennkey,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                        )
                        Profile.objects.create(user=instructor, penn_id=penn_id)
                    except:
                        instructor = None
                if instructor:
                    try:
                        NEW_INSTRUCTOR_VALUES[course_code].append(instructor)
                    except:
                        NEW_INSTRUCTOR_VALUES[course_code] = [instructor]
                else:
                    message = f"Couldn't create account for: {first_name} {last_name} | {pennkey} | {penn_id} | {email}"
                    logging.getLogger("error_logger").error(message)
        except:
            message = f"Couldn't find course {course_code}"
            logging.getLogger("error_logger").error(message)

    for course_code, instructors in NEW_INSTRUCTOR_VALUES.items():
        try:
            course = Course.objects.get(course_code=course_code)
            course.instructors.clear()
            for instructor in instructors:
                course.instructors.add(instructor)
            course.save()
        except:
            message = f"Error adding new instructor(s) to course"
            logging.getLogger("error_logger").error(message)


def crosslist_courses(term):
    pass


def available_terms():
    config = ConfigParser()
    config.read("config/config.ini")

    print(config.sections())
    info = dict(config.items("datawarehouse"))
    print(info)
    connection = cx_Oracle.connect(info["user"], info["password"], info["service"])
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT
      current_academic_term,
      next_academic_term,
      previous_academic_term,
      next_next_academic_term,
      previous_previous_acad_term
    FROM
      dwadmin.present_period"""
    )
    for x in cursor:
        print(x)


def clear_instructors(term):
    courses = Course.objects.filter(
        requested=False, course_term=term[-1], year=term[:4]
    )
    for course in courses:
        course.instructors.clear()
        course.save()


def daily_sync(term):
    pull_courses(term)
    pull_instructors(term)  # -- only for non requested courses
    # crosslisting_cleanup() -- check that for every course with a primary crosslisting that its actually crosslisted with that course
    utils.process_canvas()  # -- for each user check if they have any Canvas sites that arent in the CRF yet
    utils.update_sites_info(
        term
    )  # info # -- for each Canvas Site in the CRF check if its been altered
    delete_canceled_courses(term)


def delete_canceled_courses(term):
    config = ConfigParser()
    config.read("config/config.ini")
    domain = config.get("opendata", "domain")
    id = config.get("opendata", "id")
    key = config.get("opendata", "key")
    OData_lookup = OpenData(base_url=domain, id=id, key=key)

    # check that term is available
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
      cs.activity IN ('LEC', 'REC', 'LAB', 'SEM', 'CLN', 'CRT', 'PRE', 'STU', 'ONL', 'HYB')
    AND cs.status IN ('X')
    AND cs.tuition_school NOT IN ('WH', 'LW')
    AND cs.term= :term""",
        term=term,
    )
    # AND cs.status IN ('X','H')

    # term_varaible = str(term))
    f = open("course/static/log/deleted_courses_issues.log", "a")
    time_start = datetime.now().strftime("%Y-%m-%d")
    f.write("-----" + time_start + "-----\n")
    for (
        course_code,
        section_id,
        term,
        subject_area,
        school,
        xc,
        xc_code,
        activity,
        section_dept,
        section_division,
        title,
        status,
        rev,
    ) in cursor:
        # print(course_code, section_id, term, subject_area, school, xc, xc_code, activity, section_dept,section_division, title,status, rev)
        course_code = course_code.replace(" ", "")
        subject_area = subject_area.replace(" ", "")
        xc_code = xc_code.replace(" ", "")

        try:
            course = Course.objects.get(course_code=course_code)
            if course.requested == True:
                # does this course have course.request , course.multisection_request or course.crosslisted_request
                try:
                    canvas_site = course.request.canvas_instance
                except:
                    print("no main request:%s" % course.course_code)
                    if course.multisection_request:
                        canvas_site = course.multisection_request.canvas_instance
                    elif course.crosslisted_request:
                        canvas_site = course.crosslisted_request.canvas_instance
                    else:
                        # doesnt seem to be tied to a request.
                        canvas_site = None

                if canvas_site:
                    if canvas_site.workflow_state == "deleted":
                        # no issue
                        pass
                    else:
                        f.write(
                            "Canvas Site already Exists:" + course_code + " " + "\n"
                        )
                else:
                    f.write(
                        "Canceled Course is Requested and no Site:"
                        + course_code
                        + " "
                        + "\n"
                    )
            else:
                print("deleting ", course_code)
                course.delete()
        except:
            # the canceled course doesnt exist in the CRF... no problem for us then
            pass

    f.close()


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
  cs.activity IN ('LEC', 'REC', 'LAB', 'SEM', 'CLN', 'CRT', 'PRE', 'STU', 'ONL', 'HYB')
AND cs.status in ('O')
AND cs.term           IN (
  (
    SELECT
      previous_previous_acad_term term
    FROM
      dwadmin.present_period
  )
  ,
  (
    SELECT
      previous_academic_term term
    FROM
      dwadmin.present_period
  )
  ,
  (
    SELECT
      current_academic_term term
    FROM
      dwadmin.present_period
  )
  ,
  (
    SELECT
      next_academic_term term
    FROM
      dwadmin.present_period
  )
  ,
  (
    SELECT
      next_next_academic_term term
    FROM
      dwadmin.present_period
  )
  )
"""
