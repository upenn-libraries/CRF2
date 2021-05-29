import os
import sys
from configparser import ConfigParser

from canvasapi import Canvas

config = ConfigParser()
config.read("config/config.ini")
API_URL = config.get("canvas", "prod_env")
API_KEY = config.get("canvas", "prod_key")


def code_to_sis(course_code):
    middle = course_code[:-5][-6:]
    sis_id = "SRS_%s-%s-%s %s" % (
        course_code[:-11],
        middle[:3],
        middle[3:],
        course_code[-5:],
    )
    return sis_id


# def config_DESIGN(inputfile, outputfile):
# once the sites have been created in the CRF.
# 1. Enable Piazza
# 2. Perusall
# 3. Panopto
# 4. bump up storage quota to 3gb ( if not already )

# WHICH OF THESE TOOLS ARE AUTOMATICALLY ADDED?
# PANOPTO = "context_external_tool_90311"
# PERUSALL = "context_external_tool_223451"
# PIAZZA = "context_external_tool_????"  # automatically gets added


def SEAS_config(
    inputfile="SEAS_2020A.csv", outputfile="RESULT_GRADESCOPE_SEAS_2020A.csv"
):
    PANOPTO = "context_external_tool_90311"
    GRADESCOPE = "context_external_tool_132117"
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s,%s,%s,%s\n" % ("canvas_course_id", "course_id", "status", "Gradescope")
    )
    for line in dataFile:
        canvas_course_id, course_id, status = line.split(",")
        outFile.write("%s,%s,%s" % (canvas_course_id, course_id, status))
        try:
            canvas_course = canvas.get_course(canvas_course_id)
        except Exception:
            print("didnt find course %s" % course_id)
            canvas_course = None
        if canvas_course:
            print("canvas course: %s" % canvas_course.id)
            tabs = canvas_course.get_tabs()
            for tab in tabs:
                # CONFIGURING PANOPTO
                if tab.id == PANOPTO:
                    print("\tfound panopto")
                    try:
                        tab.update(hidden=False, position=3)
                        print("\t added panopto")
                        outFile.write(",%s" % "yes")
                    except Exception:
                        print("\tfailed panopto %s" % course_id)
                        outFile.write(",%s" % "no")
                # CONFIGURING GRADESCOPE
                if tab.id == GRADESCOPE:
                    print("\tfound panopto")
                    try:
                        tab.update(hidden=False, position=4)
                        print("\t added gradescope")
                        outFile.write(",%s" % "yes")
                    except Exception:
                        print("\tfailed panopto %s" % course_id)
                        outFile.write(",%s" % "no")
                else:
                    # skip this tab
                    pass
            outFile.write("\n")
        else:
            # finish the line in the text file
            outFile.write(",%s,%s\n" % ("site NA", "site NA"))


def SAS_teacher_info(inputfile="test2.txt", outputfile="SAS_teachers_2020B.csv"):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r")
    dataFile.readline()  # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write("canvas_id,name, email,pennkey\n")
    for line in dataFile:
        canvas_id = line.replace("\n", "")
        try:
            user = canvas.get_user(canvas_id)
            outFile.write(
                "%s,%s,%s,%s\n" % (canvas_id, user.name, user.email, user.login_id)
            )
        except Exception:
            outFile.write("%s,err,err,err\n" % (canvas_id))


def SEAS_raise_quota(outputfile="RESULT_SEAS_storage_quota.csv"):
    # quota
    # storage_quota_mb
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    # file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = [
        "1487140",
        "1493453",
        "1488890",
        "1490144",
        "1493525",
        "1493544",
        "1494663",
        "1495105",
        "1495910",
        "1494658",
        "1488896",
        "1494771",
        "1491170",
        "1495345",
        "1489898",
        "1493206",
        "1493738",
        "1495881",
        "1494074",
        "1490137",
        "1495656",
        "1495954",
        "1489852",
        "1495911",
        "1496305",
        "1495306",
        "1495114",
        "1495256",
        "1493543",
        "1491099",
        "1493409",
        "1490118",
        "1494387",
        "1493641",
        "1494351",
        "1490145",
        "1490149",
        "1493555",
        "1495344",
        "1493334",
        "1495631",
        "1495765",
        "1504523",
        "1494056",
        "1495257",
        "1490155",
        "1493255",
        "1493553",
        "1494273",
        "1494700",
        "1495940",
        "1490138",
        "1489864",
        "1495434",
        "1495176",
        "1493460",
        "1488864",
        "1484692",
        "1490156",
        "1493638",
        "1494050",
        "1495534",
        "1494981",
        "1494699",
        "1490151",
        "1486075",
        "1494220",
        "1495513",
        "1494775",
        "1496705",
        "1496258",
        "1489222",
        "1490141",
        "1494198",
        "1491266",
        "1494345",
        "1495104",
        "1495447",
        "1494382",
        "1478531",
        "1493228",
        "1494164",
        "1493455",
        "1495529",
        "1504521",
        "1494105",
        "1488889",
        "1493611",
        "1491832",
        "1495212",
        "1495970",
        "1490154",
        "1493633",
        "1491320",
        "1484812",
        "1490136",
        "1493554",
        "1496106",
        "1490116",
        "1493600",
        "1493526",
        "1493551",
        "1493601",
        "1494669",
        "1495652",
        "1491865",
        "1495022",
        "1495107",
        "1493725",
        "1494766",
        "1494576",
        "1495185",
        "1486807",
        "1494585",
        "1491806",
        "1493975",
        "1495432",
        "1487239",
        "1490135",
        "1490140",
        "1494344",
        "1503867",
        "1493454",
        "1491072",
        "1493726",
        "1494461",
        "1494989",
        "1495106",
        "1495159",
        "1493634",
        "1494618",
        "1495630",
        "1495976",
        "1488894",
        "1491566",
        "1491864",
        "1493218",
        "1494769",
        "1495431",
        "1487238",
        "1489366",
        "1490065",
        "1490143",
        "1495034",
        "1495305",
        "1497172",
        "1488895",
        "1488897",
        "1490142",
        "1490150",
        "1491268",
        "1493796",
        "1494333",
        "1494605",
        "1488863",
        "1490148",
    ]

    outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
    outFile.write(
        "%s,%s,%s,%s\n" % ("subaccount_id", "course_id", "old_quota", "new_quota")
    )
    for canvas_course_id in dataFile:

        try:
            canvas_course = canvas.get_course(canvas_course_id)
            outFile.write("%s,%s," % (canvas_course.account_id, canvas_course_id))
        except Exception:
            canvas_course = None
            outFile.write("%s,%s," % ("ERR", canvas_course_id))
        if canvas_course:
            old_quota = canvas_course.storage_quota_mb
            print("old quota ", old_quota)
            new_quota = 4000
            print("new quota ", new_quota)
            if old_quota > new_quota:
                new_quota = old_quota  # DONT LOWER THE QUOTA!!
            try:
                canvas_course.update(course={"storage_quota_mb": new_quota})
            except Exception:
                new_quota = "ERROR"
                print("\t failed to raise quota (%s)" % canvas_course_id)

            outFile.write("%s,%s\n" % (old_quota, new_quota))
        else:
            # no canvas course
            outFile.write("%s,%s\n" % ("NA", "NA"))
