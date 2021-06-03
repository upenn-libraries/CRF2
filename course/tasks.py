from __future__ import absolute_import, unicode_literals

import sys
import time
from datetime import datetime

from canvas import api as canvas_api
from datawarehouse import datawarehouse

from celery import task
from course import utils
from course.models import *
from course.serializers import RequestSerializer


@task()
def task_nightly_sync(term):
    # this task takes all of the Approved requests and attempts to make a course
    # if it doesnt work then it is locked
    # print("howdy!")
    time_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open("course/static/log/night_sync.log", "a")
    datawarehouse.daily_sync(term)
    time_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write("Nighly Update " + term + ":" + time_start + " - " + time_end + "\n")
    f.close()


@task()
def task_test():
    time_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open("course/static/log/test.log", "a")
    f.write(time_start + "\n")
    f.close()


@task()
def task_pull_courses(term):
    datawarehouse.pull_courses(term)


def update_instrutors(term):
    chain = task_clear_instructors.s(term) | task_pull_instructors.s(term)
    chain()


@task()
def task_clear_instructors(term):
    datawarehouse.clear_instructors(term)  # -- only for non requested courses


@task()
def task_pull_instructors(term):
    datawarehouse.pull_instructors(term)  # -- only for non requested courses


@task()
def task_process_canvas():
    utils.process_canvas()  # -- for each user check if they have any Canvas sites that arent in the CRF yet


@task()
def task_update_sites_info(term):
    print("term", term)
    utils.update_sites_info(
        term
    )  # info # -- for each Canvas Site in the CRF check if its been altered
    print("finished canvas site metadata update")


@task()
def task_delete_canceled_courses(term):
    datawarehouse.delete_canceled_courses(term)


# there should be a task that check all courses if they have been created in Canvas
# if they have then course.requested is set to true !

# there should be a task that checks all requests with status == Submitted if they have already been created in Canvas
# if they have been then lock the request ! and create the associated CanvasSite Instance

# def task_check_courses()


# ----------- CHECK COURSE IN CANVAS ---------------
# FREQUENCY = NIGHTLY
@task()
def task_check_courses_in_canvas():
    """
    check to see if any of the courses that do not have a request object associated with them exist yet in Canvas
    if they do then write to the file and set the course to request_override
    """
    courses = Course.objects.filter(requested=False).filter(requested_override=False)
    for course in courses:
        # if the section doesnt exist then it will return None
        found = canvas_api.find_in_canvas("SRS_" + course.srs_format())
        # found == None if there is NO CANVAS SECTION
        if found == None:
            pass  # this course doesnt exist in canvas yet
        else:
            # set the course to requested
            # course.requested_override = True
            # check that the canvas site exists in the CRF
            try:
                canvas_site = CanvasSite.objects.get(canvas_id=found.course_id)

            except:  # doesnt exist in CRF
                # Create in CRF
                canvas_site = CanvasSite
                pass


# ----------- REMOVE CANCELED REQUESTS ---------------
@task()
def delete_canceled_requests():
    _to_process = Request.objects.filter(status="CANCELED")
    for request in _to_process:
        request.delete()


# ----------- CREATE COURSE IN CANVAS ---------------
# FREQUENCY = NIGHTLY
# https://github.com/upenn-libraries/accountservices/blob/master/siterequest/management/commands/process_approved_items.py


## CREATE LOGIN -- USERNAME: PENNKEY, SIS ID: PENN_ID, fullname
@task()
def check_for_account(pennkey):
    user = canvas_api.get_user_by_sis(pennkey)
    if user == None:  # no account lets create
        try:
            crf_account = User.objects.get(username=pennkey)
            pennid = crf_account.profile.pennid
            full_name = crf_account.get_full_name()
            canvas_account = canvas_api.create_user(pennkey, pennid, fullname)
            if canvas_account:
                return canvas_account
            else:
                return None
        except:
            # log error
            pass


@task()
def create_canvas_site():
    ################### STEPS #########################
    # 1. set request to in process
    # 2. Create course in canvas ( check that is doesnt exist first )
    # 2a. Crosslist
    # 2b. add sections
    # 3. enroll faculty and additional enrollments ( check that they have accounts first)
    # 4. Configure reserves
    # 5. Content Migration
    # 6. Create CanvasSite Object and link to Request ( set canvas_instance_id )
    # 7. Set request to Complete
    # 8. Notify with email
    ####################################################
    _to_process = Request.objects.filter(status="APPROVED")
    for request_obj in _to_process:
        serialized = RequestSerializer(request_obj)
        additional_sections = (
            []
        )  # {'course_section':'','instructors':''} list of Canvas course section objects and instructors listed in CRF to use later when adding enrollments
        ######## Step 1. Set request to IN_PROCESS ########
        request_obj.status = "IN_PROCESS"
        request_obj.save()

        course_requested = request_obj.course_requested
        # input("STEP 1 DONE...\n")
        ######## Step 2. Create course in canvas ########
        account = canvas_api.find_account(
            course_requested.course_schools.canvas_subaccount
        )
        if account:  # account exists

            # check if this is not the prmary
            if (
                course_requested.course_primary_subject.abbreviation
                != course_requested.course_subject.abbreviation
            ):
                # we parse the primary!
                pc = course_requested.primary_crosslist
                if course_requested.primary_crosslist:
                    term = pc[-5:]
                    section = pc[:-5][-3:]
                    number = pc[:-5][:-3][-3:]
                    subj = pc[:-5][:-6]
                    section_name_code = "%s %s-%s %s" % (subj, number, section, term)
                else:
                    # it seems that we have a problem .primary_crosslist must be filled out
                    request_obj.process_notes += "primary_crosslist not set,"
                    request_obj.save()
                    return

            else:
                section_name_code = "%s %s-%s %s" % (
                    course_requested.course_subject.abbreviation,
                    course_requested.course_number,
                    course_requested.course_section,
                    course_requested.year + course_requested.course_term,
                )
            name_code = section_name_code
            # check if there is a title override
            if request_obj.title_override:
                name = name_code + " " + request_obj.title_override[:45]
                section_name = section_name_code + request_obj.title_override[:45]
            else:
                name = name_code + " " + course_requested.course_name
                section_name = section_name_code + " " + course_requested.course_name
            sis_course_id = "SRS_" + course_requested.srs_format_primary()
            print("sis_course_id", sis_course_id)
            print("section_name", section_name)
            term_id = canvas_api.find_term_id(
                96678, course_requested.year + course_requested.course_term
            )
            print("going to create", name, ",", sis_course_id)
            course = {
                "name": name,
                "sis_course_id": sis_course_id,
                "course_code": sis_course_id,
                "term_id": term_id,
            }
            try:
                canvas_course = account.create_course(course=course)
            except:
                # check what went wrong () !!!

                # canvas_course =
                request_obj.process_notes += (
                    "course site creation failed- check if it already exists,"
                )
                request_obj.save()
                return

            print("created", canvas_course)
            ## Raise course quota ##
            try:
                canvas_course.update(course={"storage_quota_mb": 2000})
            except:
                request_obj.process_notes += "course site quota not raised,"
                request_obj.save()

            ## Add sections ##
            #   Add main Sections
            try:

                additional_section = {"course_section": "", "instructors": ""}
                additional_section[
                    "course_section"
                ] = canvas_course.create_course_section(
                    course_section={
                        "name": section_name,
                        "sis_section_id": sis_course_id,
                    },
                    enable_sis_reactivation=True,
                )  # first_section = canvas_course.get_sections()[0]
                MAIN_SECTION = additional_section["course_section"]
                additional_section["instructors"] = course_requested.instructors.all()
                additional_sections += [additional_section]
                print(
                    "1",
                    {
                        "additional_section": additional_section,
                        "additional_sections": additional_sections,
                    },
                )
            except:
                # dont continue with the loop so just stop for now.
                print("failed to create main section,", canvas_course)
                request_obj.process_notes += "failed to create main section,"
                request_obj.process_notes += sys.exc_info()[0]
                request_obj.save()
                return
            # first_section.edit(course_section={'sis_section_id':sis_course_id},enable_sis_reactivation=True)

        else:
            request_obj.process_notes += "failed to locate Canvas Account in Canvas,"
            # error log and stop for loop
            pass
        #   Add multi-sections
        if request_obj.title_override:
            namebit = request_obj.title_override
        else:
            namebit = course_requested.course_name

        for section in serialized.data["additional_sections"]:
            section_course = Course.objects.get(course_code=section)
            if (
                section_course.course_activity.abbr != "LEC"
            ):  # dont put the name in the title, instead add the activity abbr.
                namebit = section_course.course_activity.abbr
            sis_section = "SRS_" + section_course.srs_format_primary()
            # sis_sections += [sis_section]
            try:

                additional_section = {"course_section": "", "instructors": ""}
                print(
                    {
                        "name": section_course.srs_format_primary(sis_id=False)
                        + " "
                        + namebit,
                        "sis_section_id": sis_section,
                    }
                )
                additional_section[
                    "course_section"
                ] = canvas_course.create_course_section(
                    course_section={
                        "name": section_course.srs_format_primary(sis_id=False)
                        + " "
                        + namebit,
                        "sis_section_id": sis_section,
                    },
                    enable_sis_reactivation=True,
                )
                additional_section["instructors"] = section_course.instructors.all()
                additional_sections += [additional_section]
                print(
                    "2",
                    {
                        "additional_section": additional_section,
                        "additional_sections": additional_sections,
                    },
                )

            except:
                # dont continue with the loop so just stop for now.
                request_obj.process_notes += "failed to create section,"
                request_obj.save()
                return
            # check if instructors are specified for each section

        # check for crosslist
        if course_requested.crosslisted:
            pass

        print("starting step 2")
        # input("STEP 2 DONE...\n")
        ######## Step 3. enroll faculty and additional enrollments  ########
        enrollment_types = {
            "INST": "TeacherEnrollment",
            "instructor": "TeacherEnrollment",
            "TA": "TaEnrollment",
            "ta": "TaEnrollment",
            "DES": "DesignerEnrollment",
            "designer": "DesignerEnrollment",
            "LIB": "DesignerEnrollment",
            "librarian": "DesignerEnrollment",
        }
        librarian_role_id = "1383"
        # Enroll instructors listed in SRS
        for section in additional_sections:
            for instructor in section["instructors"]:
                # check that they have an account
                user = canvas_api.get_user_by_sis(instructor.username)
                if user == None:  # user doesnt exist
                    try:
                        user = canvas_api.mycreate_user(
                            instructor.username,
                            instructor.profile.penn_id,
                            instructor.email,
                            instructor.first_name + " " + instructor.last_name,
                        )
                        request_obj.process_notes += "created account for user: %s," % (
                            instructor.username
                        )
                    except:
                        request_obj.process_notes += (
                            "failed to create account for user: %s,"
                            % (instructor.username)
                        )
                        pass  # fail silently

                # either user exists or has been created now
                try:
                    canvas_course.enroll_user(
                        user.id,
                        "TeacherEnrollment",
                        enrollment={
                            "enrollment_state": "active",
                            "course_section_id": section["course_section"].id,
                        },
                    )
                except:
                    request_obj.process_notes += "failed to add user: %s," % (
                        instructor.username
                    )
                    pass  # fail silently
                # for sect in canvas_course.get_sections():canvas_course.enroll_user(user.id, 'TeacherEnrollment' ,enrollment={'course_section_id':sect.id,'enrollment_state':'active'} )
        additional_enrollments = serialized.data["additional_enrollments"]
        # enroll custom additional enrollments - all added to MAIN SECTION ONLY
        for enrollment in additional_enrollments:
            user = enrollment["user"]
            role = enrollment["role"]
            # check if user exists
            user_canvas = canvas_api.get_user_by_sis(user)
            if user_canvas == None:  # user doesnt exist
                try:
                    user_crf = User.objects.get(username=user)
                    user_canvas = canvas_api.mycreate_user(
                        user,
                        user_crf.profile.penn_id,
                        user_crf.email,
                        user_crf.first_name + user_crf.last_name,
                    )
                    request_obj.process_notes += "created account for user: %s," % (
                        instructor.username
                    )
                except:
                    request_obj.process_notes += (
                        "failed to create account for user: %s," % (instructor.username)
                    )
                    pass  # fail silently

            if role == "LIB" or role == "librarian":
                try:
                    canvas_course.enroll_user(
                        user_canvas.id,
                        enrollment_types[role],
                        enrollment={
                            "course_section_id": MAIN_SECTION.id,
                            "role_id": librarian_role_id,
                            "enrollment_state": "active",
                        },
                    )
                except:
                    request_obj.process_notes += "failed to add user: %s," % (user)
                    pass
            else:
                try:
                    canvas_course.enroll_user(
                        user_canvas.id,
                        enrollment_types[role],
                        enrollment={
                            "course_section_id": MAIN_SECTION.id,
                            "enrollment_state": "active",
                        },
                    )
                except:
                    request_obj.process_notes += "failed to add user: %s," % (user)
                    pass
        # enroll_user(user.id ,'DesignerEnrollment' ,enrollment={'role_id':1383,'enrollment_state':'active'})
        # input("STEP 3 DONE...\n")
        ######## Step 4. Configure reserves/libguide ########
        if serialized.data["reserves"]:
            try:
                tab = canvas_api.Tab(
                    canvas_course._requester,
                    {
                        "course_id": canvas_course.id,
                        "id": "context_external_tool_139969",
                    },
                )
                tab.update(hidden=False)

                if tab.visibility != "public":
                    request_obj.process_notes += "failed to configure ARES,"
            except:
                request_obj.process_notes += "failed to try to configure ARES,"
        # input("STEP 4 DONE...\n")

        ######## Step 5. Content Migration ########
        if serialized.data["copy_from_course"]:
            contentmigration = canvas_course.create_content_migration(
                migration_type="course_copy_importer",
                settings={"[source_course_id": serialized.data["copy_from_course"]},
            )

            # need to add error reporting to this
            while (
                contentmigration.get_progress == "queued"
                or contentmigration.get_progress == "running"
            ):
                # pass
                print("still running")
                time.sleep(8)
            # if the progress is 'failed' --> report this

        # input("STEP 5 DONE...\n")
        ######## Step 6. Create CanvasSite Object and link to Request ########
        instructors = canvas_course.get_enrollments(type="TeacherEnrollment")._elements
        print("instructors ", instructors)
        _canvas_id = canvas_course.id
        _request_instance = request_obj
        _name = canvas_course.name
        _sis_course_id = canvas_course.sis_course_id
        _workflow_state = canvas_course.workflow_state
        site = CanvasSite.objects.create(
            canvas_id=_canvas_id,
            request_instance=_request_instance,
            name=_name,
            sis_course_id=_sis_course_id,
            workflow_state=_workflow_state,
        )

        request_obj.canvas_instance = site

        for instructor in instructors:
            try:
                u = User.objects.get(username=instructor)
                site.owners.add(u)
            except:
                pass
        # input("STEP 6 DONE...\n")
        ######## Step 7. Set request to Complete ########
        request_obj.status = "COMPLETED"
        request_obj.save()

        # input("STEP 7 DONE...\n")
        ######## Step 8. Notify with email ########
