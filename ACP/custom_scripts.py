from course.models import *
from datawarehouse import datawarehouse
from datawarehouse.helpers import *
import datetime
import os
from .logger import canvas_logger
from .logger import crf_logger
import sys
from configparser import ConfigParser
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
import pandas as pd


config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")  #'prod_env')
API_KEY = config.get("canvas", "prod_key")  #'prod_key')

# API_URL = "https://upenn-catalog.instructure.com"
# API_KEY = "9540~1AQ6VfHZAECvVPKQjYD1or4cUjo6NOMbc18ITOOxL5gyJiqDCUtPtqolrg7TUmWL"

########### HELPERS ################
def code_to_sis(course_code):
    middle = course_code[:-5][-6:]
    sis_id = "SRS_%s-%s-%s %s" % (
        course_code[:-11],
        middle[:3],
        middle[3:],
        course_code[-5:],
    )
    return sis_id


def find_accounts_subaccounts(account_id):
    # given an accound id (int) return a list of i
    canvas = Canvas(API_URL, API_KEY)
    subs_list = [account_id]
    account = canvas.get_account(account_id)
    subs = account.get_subaccounts(recursive=True)
    for sub in subs:
        subs_list += [sub.id]
    return subs_list


####################################
"""
 // type of quiz possible values: 'practice_quiz', 'assignment', 'graded_survey','survey'
  "quiz_type": "assignment",
"""


def count_surveys(inputfile="survey_input.csv", outputfile="RESULT_surveys.csv"):
    # canvas_course_id	course_id	short_name	canvas_account_id	term_id	status
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
        % (
            "canvas_course_id",
            "course_id",
            "account",
            "term",
            "status",
            "ungraded_surveys_published",
            "ungraded_surveys_unpublished",
            "graded_surveys_published",
            "graded_surveys_unpublished",
            "total_quizzes",
        )
    )
    # 'ungraded_surveys_published', 'ungraded_surveys_unpublished', 'graded_surveys_published','graded_surveys_unpublished'
    COUNTER = 0
    TOTAL = 11786
    for line in dataFile:
        COUNTER += 1
        if COUNTER % 25 == 0:
            print("%s/%s done" % (COUNTER, TOTAL))
        canvas_course_id, course_id, short_name, account, term, status = line.replace(
            "\n", ""
        ).split(",")
        course = canvas.get_course(canvas_course_id)
        ungraded_published = 0
        ungraded_unpublished = 0
        graded_published = 0
        graded_unpublished = 0
        total_quizzes = 0
        quizzes = course.get_quizzes()
        for quiz in quizzes:
            total_quizzes += 1
            # check ungraded
            if quiz.quiz_type == "survey":
                # check if published
                if quiz.published == True:
                    ungraded_published += 1
                else:
                    ungraded_unpublished += 1

            elif quiz.quiz_type == "graded_survey":
                # check if published
                if quiz.published == True:
                    graded_published += 1
                else:
                    graded_unpublished += 1
            else:  # quiz is not a survey
                pass
            outFile.write(
                "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                % (
                    canvas_course_id,
                    course_id,
                    account,
                    term,
                    status,
                    ungraded_published,
                    ungraded_unpublished,
                    graded_published,
                    graded_unpublished,
                    total_quizzes,
                )
            )


def temp():
    canvas = Canvas(API_URL, API_KEY)
    courses = [
        1518389,
        1518464,
        1518556,
        1518692,
        1519015,
        1519016,
        1519358,
        1519359,
        1527911,
        1528276,
        1528494,
        1528495,
        1528538,
        1528539,
        1528714,
        1528717,
        1528769,
        1528800,
        1528854,
        1528855,
        1528866,
        1528877,
        1528878,
        1528893,
        1528894,
        1528944,
        1529105,
        1529106,
        1529107,
        1529110,
        1529111,
        1529350,
        1529352,
        1530003,
        1530004,
        1530159,
        1530184,
        1530348,
        1530421,
        1532011,
        1532085,
        1532956,
        1533156,
        1533331,
        1533332,
        1533591,
        1533785,
        1534102,
        1539616,
        1540027,
        1518482,
        1534103,
        1539964,
        1540025,
        1540026,
        1540054,
        1540055,
        1541437,
        1541438,
        1541702,
        1541703,
        1542284,
        1542285,
    ]
    intern = canvas.get_user(5607930)
    for course in courses:
        canvas_course = canvas.get_course(course)
        section = canvas_course.get_sections()[0]
        canvas_course.enroll_user(
            intern.id,
            "DesignerEnrollment",
            enrollment={
                "course_section_id": section.id,
                "role_id": "1383",
                "enrollment_state": "active",
            },
        )


# canvas_course_id, sis_id, canvas_account_id = line.replace("\n","").split(",")
def add_reserves(inputfile="reserves.csv", outputfile="RESULT_Reserves.csv"):
    # this script will enable reserves given an input file that contains only one column ( the sis id)
    # if reserves are already enabled it wil note that and not update the site.
    RESERVES = "context_external_tool_139969"
    SUB_ACCOUNTS = [99237, 128877, 99244, 99238, 99239, 99240, 99242]
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s,%s,%s,%s\n" % ("canvas_course_id", "course_id", "account", "Reserves")
    )

    ## build a list of sub account's sub accounts
    SUB_SUB_ACCOUNTS = []
    for sub in SUB_ACCOUNTS:
        SUB_SUB_ACCOUNTS += find_accounts_subaccounts(sub)

    print(SUB_SUB_ACCOUNTS)
    # return SUB_SUB_ACCOUNTS

    for line in dataFile:
        # canvas_course_id	course_id	canvas_account_id
        canvas_course_id, sis_id, canvas_account_id = line.replace("\n", "").split(",")
        outFile.write("%s, %s, %s" % (canvas_course_id, sis_id, canvas_account_id))
        if int(canvas_account_id) in SUB_SUB_ACCOUNTS:
            try:
                canvas_course = canvas.get_course(canvas_course_id)
                print("\t found course ", canvas_course)

            except:
                print("\t didnt find course %s" % canvas_course_id)
                canvas_course = None

        else:
            print("course %s not in opt in school" % (canvas_account_id))
            canvas_course = False

        if canvas_course:
            print("canvas course: %s" % canvas_course.id)
            tabs = canvas_course.get_tabs()
            for tab in tabs:
                # CONFIGURING RESERVES
                if tab.id == RESERVES:
                    print("\tfound Reserves")
                    # outFile.write(",%s\n" % 'already added')
                    try:
                        if tab.visibility != "public":
                            tab.update(hidden=False, position=3)
                            print("\t enabled reserves")
                            outFile.write(",%s\n" % "added")

                        else:
                            print("\t already enabled reserves ")
                            outFile.write(",%s\n" % "already added")
                    except:
                        print("\tfailed reserves %s" % canvas_course_id)
                        outFile.write(",%s\n" % "failed to add")
                else:
                    # skip this tab
                    pass
            # outFile.write("\n")
        elif canvas_course == None:  # no site
            outFile.write(",%s\n" % "couldnt find")
        elif canvas_course == False:  # not in program
            outFile.write(",%s\n" % "not in program")
        else:
            print("HEY YOU SHOULDNT GET TO THIS CASE", canvas_course_id)
    print("be sure to add the RESULT_.csv to the Master file")


# add_reserves(inputfile='testing_courses.csv')
def quick_add_reserves(canvas_id):
    canvas = Canvas(API_URL, API_KEY)
    RESERVES = "context_external_tool_139969"
    try:
        canvas_course = canvas.get_course(canvas_id)
    except:
        return "couldnt find course"
    tabs = canvas_course.get_tabs()
    for tab in tabs:
        # CONFIGURING RESERVES
        if tab.id == RESERVES:
            print("\tfound Reserves")
            try:
                if tab.visibility != "public":
                    tab.update(hidden=False, position=3)
                    print("\t enabled reserves")
                else:
                    print("\t already enabled reserves ")
            except:
                print("\tfailed reserves %s" % canvas_id)
        else:
            # skip this tab
            pass


def raise_quota(
    inputfile="storage_quota.csv",
    outputfile="RESULT_storage_quota.csv",
    incr=1000,
    use_sis_id=False,
):
    # quota raise step 2
    # storage_quota_mb
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s,%s,%s,%s\n" % ("subaccount_id", "course_id", "old_quota", "new_quota")
    )
    for line in dataFile:

        if use_sis_id and line[:4] != "SRS_":
            canvas_course_id = code_to_sis(line.replace("\n", ""))
        else:
            canvas_course_id = line.replace("\n", "")

        try:
            canvas_course = canvas.get_course(canvas_course_id, use_sis_id=use_sis_id)
            outFile.write("%s,%s," % (canvas_course.account_id, canvas_course_id))
        except:
            canvas_course = None
            outFile.write("%s,%s," % ("ERR", canvas_course_id))
        if canvas_course:
            old_quota = canvas_course.storage_quota_mb
            print("old quota ", old_quota)
            new_quota = old_quota + incr
            print("new quota ", new_quota)
            try:
                canvas_course.update(course={"storage_quota_mb": new_quota})
            except:
                new_quota = "ERROR"
                print("\t failed to raise quota (%s)" % canvas_course_id)

            outFile.write("%s,%s\n" % (old_quota, new_quota))
        else:
            # no canvas course
            outFile.write("%s,%s\n" % ("NA", "NA"))


def create_quota_file(
    inputfile="mystorage_quota.csv",
    outputfile="storage_quota.csv",
    incr=1000,
    use_sis_id=False,
):
    # quota raise step 1
    # storage_quota_mb
    # make sure you remove the unnecessary columns and then filter by storage used >80
    SUB_ACCOUNTS = [
        "132477",
        "99243",
        "99237",
        "132280",
        "107448",
        "132413",
        "128877",
        "99241",
        "99244",
        "99238",
        "99239",
        "131752",
        "131428",
        "99240",
        "132153",
        "82192",
    ]
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("sis_id\n")
    counter = 1
    for line in dataFile:
        # print(counter)
        # counter +=1
        canvas_id, sis_id, account_id, storage_used, all_used = line.replace(
            "\n", ""
        ).split(",")
        if account_id in SUB_ACCOUNTS:
            try:
                canvas_course = canvas.get_course(canvas_id)
                # print(canvas_id,storage_used,canvas_course.storage_quota_mb)
                percentage_used = float(storage_used) / round(
                    int(canvas_course.storage_quota_mb)
                )
                # print("\t percentage used ",percentage_used)
                if percentage_used >= 0.79:
                    if sis_id:
                        print("\t %s needs to be increased" % sis_id)
                        outFile.write("%s\n" % sis_id)
                    else:
                        print("\t %s needs to be increased (NO SIS ID!)" % canvas_id)
            except:
                print("couldnt find course %s" % sis_id)
    print("raise_quota(use_sis_id=True)")


"""
    ~~~~ THE STEPS IN RUNNING THE UNCONFIRMED EMAILS ~~~~

0. Run Provisioning Report ___ and delete all columns but the canvas_user_id
1. find_unconfirmed_emails()
2. unconfirmed_email_check_school() 
3. Create a new file from the output of 2 and filter to the schools we can remediate
4. Run verify_email_list() *
5. Check errors from output
6. Check the schools we can't remediate (from 3.) by hand to confirm we cant remediate. send list to the schools

"""


def find_unconfirmed_emails(
    inputfile="2020A_Enrollments.csv", outputfile="RESULT_2020A_Enrollments.csv"
):
    total = 26316  # hard coded
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "a")
    outFile.write("%s,%s\n" % ("canvas_user_id", "email_status"))
    counter = 1
    for line in dataFile:
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))
        canvas_user_id = line.replace("\n", "")
        user = canvas.get_user(canvas_user_id)
        email_status = "NONE"
        communication_channels = user.get_communication_channels()
        for c in communication_channels:
            # we only want the first one!
            try:
                email_status = c.workflow_state
            except:
                pass
            break

        if email_status == "NONE" or email_status == "unconfirmed":
            outFile.write("%s,%s\n" % (canvas_user_id, email_status))

        counter += 1


def unconfirmed_email_check_school(
    inputfile="RESULT_2020A_Enrollments.csv",
    outputfile="REMEDIATE_2020A_Enrollments.csv",
):
    # given the unconfirmed emails list, checks in the original file if they have multiple enrollments
    # if they have multiple enrollments, check if any all of the enrollments are in schools we do not support
    # if this is the case, write this user down in a separate file
    # otherwise, write them in a file that will then be remediated.
    total = 5893  # HARDCODED
    SUB_ACCOUNTS = []
    ACCOUNTS = [
        "99243",
        "99237",
        "128877",
        "99241",
        "99244",
        "99238",
        "99239",
        "131428",
        "99240",
        "132153",
        "82192",
    ]
    for a in ACCOUNTS:
        SUB_ACCOUNTS += find_accounts_subaccounts(int(a))
    print(SUB_ACCOUNTS)
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("%s,%s,%s\n" % ("canvas_user_id", "email_status", "can_remediate"))
    counter = 1
    for line in dataFile:
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))

        canvas_user_id, email_status = line.replace("\n", "").split(",")
        user = canvas.get_user(canvas_user_id)
        user_enrollments = user.get_courses()  # should we limit by term?
        can_fix = False
        for course in user_enrollments:
            try:
                if str(course.account_id) in SUB_ACCOUNTS:
                    can_fix = True
                    break  # will this stop from iterating through the rest of the list?
            except:
                print("\t (%s) error with user %s" % (counter, canvas_user_id))
            # check if the account id is in the list of sub accounts
            # if it is not_supported_school = False

        # we can remediate this user's account if the final column is False!
        outFile.write("%s,%s,%s\n" % (canvas_user_id, email_status, can_fix))
        counter += 1


def verify_email_list(inputfile, outputfile="Errors_Emails.txt"):
    total = 445  # HARDCODED
    # canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("%s,%s\n" % ("canvas_user_id", "email_status"))
    counter = 0
    for line in dataFile:
        counter += 1
        print(counter)
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))
        user_id = line.replace("\n", "")
        try:
            is_verified = verify_first_email(int(user_id))
            if is_verified:
                outFile.write("%s,%s\n" % (user_id, "confirmed"))
            else:
                outFile.write("%s,%s\n" % (user_id, "needs check"))
        except:

            outFile.write("%s,%s\n" % (user_id, "error"))


def check_dummy_email_deleted(user_id):
    DUMMY = "test@gmail.com"
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_user(user_id)
    communication_channels = user.get_communication_channels()
    found = False
    for comm_channel in communication_channels:
        if comm_channel.address == DUMMY:
            found = True
            if comm_channel.workflow_state == "deleted":
                return True
            else:
                return False  # ahh it is stll active!

    if found:
        print("\t Dummy email wasnt deleted for user %s" % (user_id))
        return False
    else:
        return True


def check_verified_email(user_id, address):
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_user(user_id)
    communication_channels = user.get_communication_channels()
    for comm_channel in communication_channels:
        if comm_channel.address == address:
            # return True if workflow
            if comm_channel.workflow_state == "active":
                return True
            else:
                return False
    print("\t Couldn't find former email %s for user %s" % (address, user_id))
    return False


def verify_first_email(user_id):
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_user(user_id)
    communication_channels = user.get_communication_channels()
    for comm_channel in communication_channels:
        # verify the first one by re-creating it but auto-verify the new one
        if comm_channel.type == "email":
            dummy_channel = user.create_communication_channel(
                communication_channel={"address": "test@gmail.com", "type": "email"},
                skip_confirmation=True,
            )
            # print(dummy_channel.to_json())
            email = comm_channel.address
            # print(comm_channel.to_json())
            comm_channel.delete()
            new_channel = user.create_communication_channel(
                communication_channel={"address": email, "type": "email"},
                skip_confirmation=True,
            )
            dummy_channel.delete()

            # check that email is verified
            email_is_verified = check_verified_email(user_id, email)
            if email_is_verified == False:
                print("\t email not verified for user %s" % user_id)

            # check that dummy is deleted
            dummy_is_deleted = check_dummy_email_deleted(user_id)
            if dummy_is_deleted == False:
                print("\t dummy not deleted for user %s" % user_id)

            if dummy_is_deleted and email_is_verified:
                return True
            else:
                return False
        break

    return False


def libGuideUsage(inputfile, outputfile="LibGuides_Canvas_2020A.csv"):
    total = 6124  # HARDCODED
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("%s,%s,%s\n" % ("canvas_course_id", "course_id", "libguide"))
    counter = 0
    for line in dataFile:
        counter += 1
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))

        canvas_course_id, course_sis_id, canvas_account_id, status = line.replace(
            "\n", ""
        ).split(",")
        try:
            canvas_course = canvas.get_course(canvas_course_id)
            tabs = canvas_course.get_tabs()
            libguide = False
            for tab in tabs:
                if tab.id == "context_external_tool_89961":
                    # print(course_sis_id, tab.id,tab.label,tab.visibility)
                    if tab.visibility == "admins":  # the tab is not active
                        pass
                    else:
                        libguide = True
                    break  # dont continue with the loop!

            outFile.write("%s,%s,%s\n" % (canvas_course_id, course_sis_id, libguide))
        except:
            outFile.write("%s,%s,%s\n" % (canvas_course_id, course_sis_id, "ERROR"))


def hide_final_grades(inputfile, outputfile="RESULT_hide_grades.csv"):
    # not finished
    canvas = Canvas(API_URL, API_KEY)
    total = 1  # HARDCODED
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("%s,%s,%s\n" % ("canvas_user_id", "email_status", "can_remediate"))
    counter = 1
    for line in dataFile:
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))

    # course.update(course={'hide_final_grades':True})


def recent_course_activity(
    inputfile="course_list.csv", outputfile="recent_activity.csv"
):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "course_id,account_id,account_name,storage,last_activity_instructor,last_activity_student,end_at\n"
    )
    for line in dataFile:
        overall_last_activity_inst = "0"
        overall_last_activity_stud = "0"
        course_id, account_id, account_name, storage_used = line.replace(
            "\n", ""
        ).split(",")
        canvas_site = canvas.get_course(course_id)
        s_users = canvas_site.get_enrollments(type=["StudentEnrollment"])
        i_users = canvas_site.get_enrollments(type=["TeacherEnrollment"])

        if canvas_site.end_at:
            end_at = canvas_site.end_at
        else:
            end_at = "None"

        for student in s_users:
            last_activity = student.last_activity_at
            try:
                # print("\t",overall_last_activity,last_activity)
                if last_activity > overall_last_activity_stud:
                    overall_last_activity_stud = last_activity
            except:
                pass
                # print("\t",course_id, user.user_id,last_activity)

        for instructor in i_users:
            last_activity = instructor.last_activity_at
            try:
                # print("\t",overall_last_activity,last_activity)
                if last_activity > overall_last_activity_inst:
                    overall_last_activity_inst = last_activity
            except:
                pass
                # print("\t",course_id, user.user_id,last_activity)

        print(
            course_id,
            account_id,
            account_name,
            storage_used,
            overall_last_activity_stud,
            overall_last_activity_inst,
        )
        outFile.write(
            "%s,%s,%s,%s,%s,%s,%s\n"
            % (
                course_id,
                account_id,
                account_name,
                storage_used,
                overall_last_activity_inst,
                overall_last_activity_stud,
                end_at,
            )
        )

    return


def test():
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(1494867)
    tabs = course.get_tabs()
    counter = 1
    libguide = False
    for tab in tabs:
        print(counter)
        if tab.id == "context_external_tool_89961":
            print(tab.id, tab.label, tab.visibility)
            if tab.visibility == "admins":
                pass  # the tab is not active
            else:
                libguide = True
            break
        counter += 1
    print(counter, libguide)


"""
~~~~~~~~~~~~ COURSE SHOPPING ~~~~~~~~~~~~~~~~
get a provisioning report of all courses
1.delete all columns but: canvas_id, sis_id,short_name, account_id,status
2. delete all rows with blank sis_ids
3. compare with master and remove and previously seen courses
4. create one file for WH (sis_id !startwith SRS_) and one for rest 
5. run enable_course_shopping() on non wharton file
6. run WHARTON_enable_course_shopping() on wharton file 
7. upload each file results to pennbox
8. add newly enabled to MASTER
9. upload new version of MASTER

"""


def WH_linked_to_SRS(canvas_id):
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(canvas_id)
    sections = course.get_sections()
    # check that a section has a SIS_ID starting with "SRS_"
    for s in sections:
        try:
            if s.sis_section_id.startswith("SRS_"):
                return True
        except:
            pass
    return False


def linked_to_SRS(course_id):
    # check that there is a section in the course with an SIS ID that begins with "SRS_"
    # "in_SRS = linked_to_SRS(canvas_id)"
    return course_id.startswith("SRS_")


def WHARTON_enable_course_shopping(
    inputfile, outputfile="WH_2020C_courses_shopping_enabled.csv"
):

    canvas = Canvas(API_URL, API_KEY)
    # Do feel free to target account id 81471, SIS ID WHARTON
    WHARTON_ACCOUNT_ID = 81471
    WHARTON_ACCOUNTS = find_accounts_subaccounts(WHARTON_ACCOUNT_ID)
    WH_EXCLUDE = [
        1533534,
        1544662,
        1545833,
        1546333,
        1546334,
        1546014,
        1534322,
        1545633,
        1545551,
        1545538,
        1530182,
        1541427,
        1545959,
        1528661,
        1533373,
        1541391,
        1541392,
        1541393,
        1541394,
        1541395,
        1541396,
        1541397,
        1541398,
        1541399,
        1541400,
        1541401,
        1541402,
        1540185,
        1540186,
        1532920,
        1540130,
        1539621,
        1540008,
        1544660,
        1541461,
        1533499,
        1533500,
        1540120,
        1527591,
        1546010,
        1542201,
        1544821,
        1542311,
        1545547,
        1544274,
        1540000,
        1539655,
        1544059,
        1533358,
        1544488,
        1533036,
        1531945,
        1529286,
        1544482,
        1534136,
        1544273,
        1540001,
        1544321,
        1533037,
        1540131,
        1539623,
        1541203,
        1529372,
        1527672,
        1543902,
        1534137,
        1518420,
        1532973,
        1532776,
        1533100,
        1532958,
        1518436,
        1532774,
        1533171,
        1532959,
        1534144,
        1542115,
        1512130,
        1545744,
        1542523,
        1542524,
        1542525,
        1542526,
        1542527,
        1543845,
        1542530,
        1542531,
        1542532,
        1542533,
        1542534,
        1542535,
        1543846,
        1542540,
        1532930,
        1512304,
        1526396,
        1527421,
        1527428,
        1507562,
    ]

    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("sis_id, canvas_id, visibility_status, published, notes\n")
    total = 3145  # HARDCODED !!!

    counter = 0
    for line in dataFile:
        counter += 1
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))
        ### ASSUMES ALL FIELDS ARE POPULATED  ###
        canvas_id, sis_id, short_name, account_id, status = line.replace(
            "\n", ""
        ).split(",")
        notes = ""
        canvas_course = None
        try:
            canvas_course = canvas.get_course(canvas_id)
            published = status
        except:

            notes = "couldnt find course"
            published = "ERROR"

        if canvas_course:
            if (
                int(account_id) not in WHARTON_ACCOUNTS
            ):  # then we should not update this site!!!!
                print("\t school not participating")
                notes += "/ NOT WHARTON"
                outFile.write(
                    "%s, %s, %s, %s, %s\n"
                    % (sis_id, canvas_id, status, published, notes)
                )

            else:  # account id in WHARTON_ACCOUNTS
                update = False
                try:
                    # see if the course is connected to SRS
                    print("\t", canvas_id, sis_id, short_name, account_id, status)
                    update = False
                    in_SRS = WH_linked_to_SRS(canvas_id)
                    if in_SRS == False:
                        print("\t not in SRS")
                        notes += "\ not liked to SRS"
                        update = False
                    elif int(canvas_id) in WH_EXCLUDE:
                        print("\t single site to ignore")
                        notes += "\ in exclude list"
                        update = False
                    else:  # we know the course is connected to SRS and not a special ignore site
                        update = True
                except:
                    print("ERROR WITH COURSE: ", sis_id, canvas_id)
                    outFile.write(
                        "%s, %s, %s, %s, %s\n"
                        % (sis_id, canvas_id, "err", "err", "err")
                    )

                if update:
                    print("\t\tshould update course")
                    try:
                        canvas_course.update(course={"is_public_to_auth_users": True})
                        status = "public_to_auth_users"
                    except:
                        status = "ERROR"

                    print(sis_id, canvas_id, status, published, notes)
                outFile.write(
                    "%s, %s, %s, %s, %s\n"
                    % (sis_id, canvas_id, status, published, notes)
                )

    """

            # NEED TO SWAP ALL THE FALSES TO TRUES
            # Check if in Wharton
            if int(account_id) in WHARTON_ACCOUNTS:
                # check if linked to SRS -- use helper function
                in_SRS = linked_to_SRS(course_id)
                # STILL NEED TO MAKE CASE FOR EXECUTIVE MBA
                if in_SRS == True: 
                    update = True
            else:
                #CHeck if course's sections are associated with SRS (
    """


# enable_course_shopping('provisioning_csv_08_31.csv')


def enable_course_shopping(inputfile, outputfile="2020C_courses_shopping_enabled.csv"):
    # REMEBER TO FILL IN ANY BLANKS FOR THE COURSE_ID!!!
    # sub accounts that have opt-ed IN
    canvas = Canvas(API_URL, API_KEY)
    # sub Accounts to ignore
    SAS_ONL_ACCOUNT = 132413
    ADMIN_ACCOUNT = 131963

    WHARTON_ACCOUNT_ID = 81471
    WHARTON_ACCOUNTS = find_accounts_subaccounts(WHARTON_ACCOUNT_ID)

    SAS_ACCOUNT_ID = 99237
    SAS_ACCOUNTS = find_accounts_subaccounts(SAS_ACCOUNT_ID)
    SAS_ACCOUNTS.remove(SAS_ONL_ACCOUNT)
    SAS_ACCOUNTS.remove(ADMIN_ACCOUNT)

    SEAS_ACCOUNT_ID = 99238
    SEAS_ACCOUNTS = find_accounts_subaccounts(SEAS_ACCOUNT_ID)

    NURS_ACCOUNT_ID = 99239
    NURS_ACCOUNTS = find_accounts_subaccounts(NURS_ACCOUNT_ID)

    AN_ACCOUNT_ID = 99243
    AN_ACCOUNTS = find_accounts_subaccounts(AN_ACCOUNT_ID)

    SUB_ACCOUNTS = (
        SAS_ACCOUNTS + SEAS_ACCOUNTS + NURS_ACCOUNTS + AN_ACCOUNTS
    )  # WHARTON_ACCOUNTS +
    print(SUB_ACCOUNTS)
    # SUBJECTS TO IGNORE
    SUBJ_TO_IGNORE = ["MAPP", "IMPA", "DYNM"]
    # INDIVIDUAL SITES TO IGNORE
    SINGLE_SITES_TO_IGNORE = ["1529220"]

    # canvas = Canvas("https://upenn.beta.instructure.com", "25~SEUFg2kAnCcarRFHAKTH1H7NIEFu7cEGeKrf2gNGkjAZTzElglrqGiVOlq5BfdKK")
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("sis_id, canvas_id, visibility_status, published, notes\n")
    total = 3145  # HARDCODED !!!
    counter = 0
    for line in dataFile:
        counter += 1
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))

        # canvas_course_id, course_id, short_name, canvas_account_id, status
        ### ASSUMES ALL FIELDS ARE POPULATED  ###
        canvas_id, sis_id, short_name, account_id, status = line.replace(
            "\n", ""
        ).split(",")
        notes = ""
        canvas_course = None
        try:
            canvas_course = canvas.get_course(canvas_id)
            published = status
        except:

            notes = "couldnt find course"
            published = "ERROR"

        if canvas_course:
            if (
                int(account_id) not in SUB_ACCOUNTS
            ):  # then we should not update this site!!!!
                print("\t school not participating")
                notes += "/ subaccount opt out"
                outFile.write(
                    "%s, %s, %s, %s, %s\n"
                    % (sis_id, canvas_id, status, published, notes)
                )

            else:  # lets update this site babie
                try:
                    print("\t", canvas_id, sis_id, short_name, account_id, status)
                    update = False
                    in_SRS = linked_to_SRS(sis_id)
                    if in_SRS == False:
                        print("\t not in SRS")
                        update = False
                    elif int(canvas_id) in SINGLE_SITES_TO_IGNORE:
                        print("\t single site to ignore")

                        update = False
                    else:  # we know the course is connected to SRS and not a special ignore site
                        course_number = sis_id.split("-")[
                            1
                        ]  # need a way to double check this...!
                        subj = sis_id.split("-")[0][4:]
                        print("\t COURSE NUMBER: ", course_number)
                        print("\t SUBJ : ", subj)
                        # check if SEAS
                        if int(account_id) in SEAS_ACCOUNTS:
                            # SEAS wants to enable shopping for all courses
                            update = True
                        else:  # not SEAS
                            if int(account_id) in NURS_ACCOUNTS:
                                # check course number - if course >= 600 then ignore
                                # course_number = sis_id.split("-")[1] # need a way to double check this...!
                                if int(course_number) <= 600:
                                    update = True

                            elif (
                                int(account_id) in SAS_ACCOUNTS
                                and int(course_number) <= 500
                            ):  # in SAS and undergrad
                                # check if subject in ignore list
                                if subj in SUBJ_TO_IGNORE:
                                    print("\t subj to ignore")
                                    update = False
                                else:
                                    update = True

                            elif (
                                int(account_id) in AN_ACCOUNTS
                                and int(course_number) <= 500
                            ):
                                if subj == "COMM":  # only update these
                                    update = True
                                else:
                                    update = False
                            else:
                                update = False

                except:
                    print("ERROR WITH COURSE: ", sis_id, canvas_id)
                    outFile.write(
                        "%s, %s, %s, %s, %s\n"
                        % (sis_id, canvas_id, "err", "err", "err")
                    )

                if update:
                    print("\t\tshould update course")
                    try:
                        canvas_course.update(course={"is_public_to_auth_users": True})
                        status = "public_to_auth_users"
                    except:
                        status = "ERROR"

                    print(sis_id, canvas_id, status, published, notes)
                    outFile.write(
                        "%s, %s, %s, %s, %s\n"
                        % (sis_id, canvas_id, status, published, notes)
                    )


def disable_course_shopping(inputfile, outputfile):
    # once the enabled script has been tested , just copy n paste...
    # REMEBER TO FILL IN ANY BLANKS FOR THE COURSE_ID/NOTES!!!

    # sub accounts that have opt-ed out these should be filtered out before running the script
    # MEHP 132097 132098 132100 132099
    # PSOM 99242
    # SUB_ACCOUNTS = [132097, 132098, 132100, 132099, 99242] # you should remove these before running the script -- but i'll code it anyways just in case...
    canvas = Canvas(API_URL, API_KEY)
    # canvas = Canvas("https://upenn.beta.instructure.com", "25~SEUFg2kAnCcarRFHAKTH1H7NIEFu7cEGeKrf2gNGkjAZTzElglrqGiVOlq5BfdKK")
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("sis_id, canvas_id, visibility_status, published, notes\n")
    total = 692  # HARDCODED !!!
    counter = 0
    for line in dataFile:
        counter += 1
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))

        # sis_id	 canvas_id	 visibility_status	 published
        # print(line)
        canvas_id, sis_id, status = line.replace("\n", "").split(",")
        notes = ""
        try:
            canvas_course = canvas.get_course(canvas_id)
            published = status
        except:
            notes = "couldnt find course"
            published = "ERROR"

        # if int(account_id) in SUB_ACCOUNTS: # then we should not update this site!!!!
        #    notes += "/ subaccount opt out"
        #    outFile.write("%s, %s, %s, %s, %s\n" % (sis_id, canvas_id, status, published, notes))

        # else: # lets update this site babie
        try:
            # print('\t',visibility_status, visibility_status=='public_to_auth_users')
            # if visibility_status == ' public_to_auth_users' or visibility_status='public_to_auth_users':
            canvas_course.update(
                course={
                    "is_public": False,
                    "is_public_to_auth_users": False,
                    "public_syllabus": False,
                    "public_syllabus_to_auth": False,
                }
            )
            status = "to_enrolled_users"  # change this please
            # else:
            #    print("not updating %s course" % sis_id)
            #    status = visibility_status
        except:
            status = "ERROR"

        print(sis_id, canvas_id, status, published, notes)
        outFile.write(
            "%s, %s, %s, %s, %s\n" % (sis_id, canvas_id, status, published, notes)
        )


def countEnrollments(
    inputfile="NEW_NEWcanvasSitesFile.txt",
    outputfile="ProvisionedSitesEnrollmentCount.csv",
):
    canvas = Canvas(API_URL, API_KEY)
    total = 3042
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s,%s,%s\n" % ("canvas_id", "student_enrollments", "instructor_enrollments")
    )
    counter = 0
    for line in dataFile:
        counter += 1
        if counter % 25 == 0:
            print("%s/%s done" % (counter, total))

        student_count = 0
        instructor_count = 0
        course_code, canvas_id = line.split(",")
        try:  # well if there is no Canvas course.
            course = canvas.get_course(canvas_id)
            try:
                student_enrollments = course.get_enrollments(type=["StudentEnrollment"])
            except:
                student_enrollments = []
            try:
                instructor_enrollments = course.get_enrollments(
                    type=["TeacherEnrollment"]
                )
            except:
                instructor_enrollments = []

            for s_e in student_enrollments:
                student_count += 1

            for i_e in instructor_enrollments:
                instructor_count += 1

            print(canvas_id, student_count, instructor_count)
            outFile.write("%s,%s,%s\n" % (canvas_id, student_count, instructor_count))
        except:
            outFile.write("%s,%s,%s\n" % (canvas_id, "ERR", "ERR"))


def deleteCourses(inputfile="test2.txt"):
    canvas = Canvas(API_URL, API_KEY)
    total = 439
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    for line in dataFile:
        course_id = line.replace("\n", "")
        course = canvas.get_course(course_id)
        isDeleted = course.delete()
        if not isDeleted:
            print("couldn't delete course", course)
