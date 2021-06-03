from __future__ import print_function

from configparser import ConfigParser
from datetime import datetime
from logging import getLogger
from re import findall
from string import capwords

import cx_Oracle

from course import utils
from course.models import Activity, Course, Profile, School, Subject, User
from OpenData.library import OpenData


def get_cursor():
    config = ConfigParser()
    config.read("config/config.ini")
    values = dict(config.items("datawarehouse"))
    connection = cx_Oracle.connect(
        values["user"], values["password"], values["service"]
    )
    return connection.cursor()


def get_open_data():
    config = ConfigParser()
    config.read("config/config.ini")
    values = dict(config.items("opendata"))
    return OpenData(base_url=values["domain"], id=values["id"], key=values["key"])


def roman_title(title):
    roman_numeral = findall(r" [MDCLXVI]+", title)
    title = capwords(title)
    if roman_numeral:
        title = title.replace(roman_numeral[-1].upper(), roman_numeral[-1][1:])
    return title


def get_user(penn_id):
    cursor = get_cursor()
    cursor.execute(
        """
        SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENNKEY
        FROM EMPLOYEE_GENERAL
        WHERE PENN_ID= :penn_id """,
        penn_id=str(penn_id),
    )
    for first_name, last_name, email, pennkey in cursor:
        return [first_name, last_name, email, pennkey]


def pull_courses(term):
    open_data = get_open_data()
    cursor = get_cursor()
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
      cs.activity IN (
        'LEC', 'REC', 'LAB', 'SEM', 'CLN', 'CRT', 'PRE', 'STU', 'ONL', 'HYB'
        )
    AND cs.tuition_school NOT IN ('WH', 'LW')
    AND cs.status in ('O')
    AND cs.term = :term""",
        term=term,
    )

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

        course_code = course_code.replace(" ", "")
        primary_crosslist = ""
        subject_area = subject_area.replace(" ", "")
        xc_code = xc_code.replace(" ", "")
        # print("subject_area", subject_area)
        # print("adding ", course_code)
        try:
            subject = Subject.objects.get(abbreviation=subject_area)
        except:
            getLogger("error_logger").error("couldnt find subject %s ", subject_area)
            print("trouble finding subject: ", subject_area)
            school_code = open_data.find_school_by_subj(subject_area)
            if school_code:
                try:
                    school = School.objects.get(opendata_abbr=school_code)
                    # NEEDS TO GET SUBJECT AREA NAME
                    subject = Subject.objects.create(
                        abbreviation=subject_area, name=subject_area, schools=school
                    )
                except:
                    # print("couldn't find school ", school_code)
                    pass

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
                getLogger("error_logger").error("couldnt find subject %s ", p_subj)
                print("trouble finding primary subject: ", p_subj)
                school_code = open_data.find_school_by_subj(p_subj)
                school = School.objects.get(opendata_abbr=school_code)
                primary_subject = Subject.objects.create(
                    abbreviation=p_subj, name=p_subj, schools=school
                )
        else:
            # print("crosslist_primary", xc_code, "not found")
            primary_subject = subject

        school = primary_subject.schools
        try:
            activity = Activity.objects.get(abbr=activity)
        except:
            getLogger("error_logger").error("couldnt find activity %s ", activity)
            activity = Activity.objects.create(abbr=activity, name=activity)

        try:
            n_s = course_code[:-5][-6:]
            course_number = n_s[:3]
            section_number = n_s[-3:]
            roman_numeral = findall(r"[MDCLXVI]+", title)
            title = capwords(title)
            if roman_numeral:
                title = roman_title(title)
            year = term[:4]

            Course.objects.update_or_create(
                course_code=course_code,
                defaults={
                    "owner": User.objects.get(username="mfhodges"),
                    "course_term": term[-1],
                    "course_activity": activity,
                    "course_subject": subject,
                    "course_primary_subject": primary_subject,
                    "primary_crosslist": primary_crosslist,
                    "course_schools": school,
                    "course_number": course_number,
                    "course_section": section_number,
                    "course_name": title,
                    "year": year,
                },
            )

        except Exception as e:
            # check if updates !
            # 1. check if the course exists
            #   a. find the course
            #   b. check if the primary_crosslist and course_primary_subject
            #   needs to be updated
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

            print(type(e), e.__cause__, e)

            # course doesnt already exist
            #    print(type(e),e.__cause__)
            #    #getLogger("error_logger").error("couldnt add course %s
            #    #",datum["section_id"])
    print("DONE LOADING COURSES")

    # check if it already exists


def pull_instructors(term):
    cursor = get_cursor()
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
            if not course.requested:
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
                    message = (
                        f"Couldn't create account for: {first_name} "
                        f"{last_name} | {pennkey} | {penn_id} | {email} | {section_id}"
                    )
                    getLogger("error_logger").error(message)
        except:
            message = f"Couldn't find course {course_code}"
            getLogger("error_logger").error(message)

    for course_code, instructors in NEW_INSTRUCTOR_VALUES.items():
        try:
            course = Course.objects.get(course_code=course_code)
            course.instructors.clear()
            for instructor in instructors:
                course.instructors.add(instructor)
            course.save()
        except:
            message = "Error adding new instructor(s) to course"
            getLogger("error_logger").error(message)


def available_terms():
    cursor = get_cursor()
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


def daily_sync(term):
    pull_courses(term)
    pull_instructors(term)
    utils.process_canvas()
    utils.update_sites_info(
        term
    )  # info # -- for each Canvas Site in the CRF check if its been altered
    delete_canceled_courses(term)


def delete_canceled_courses(term):
    cursor = get_cursor()
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
      cs.activity IN (
        'LEC', 'REC', 'LAB', 'SEM', 'CLN', 'CRT', 'PRE', 'STU', 'ONL', 'HYB'
        )
    AND cs.status IN ('X')
    AND cs.tuition_school NOT IN ('WH', 'LW')
    AND cs.term= :term""",
        term=term,
    )
    # AND cs.status IN ('X','H')

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
        # print(course_code, section_id, term, subject_area, school, xc,
        # xc_code, activity, section_dept,section_division, title,status, rev)
        course_code = course_code.replace(" ", "")
        subject_area = subject_area.replace(" ", "")
        xc_code = xc_code.replace(" ", "")

        try:
            course = Course.objects.get(course_code=course_code)
            if course.requested:
                # does this course have course.request ,
                # course.multisection_request or course.crosslisted_request
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
