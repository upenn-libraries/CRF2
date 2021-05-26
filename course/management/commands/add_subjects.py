import json
import logging
from configparser import ConfigParser

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from course.models import School, Subject
from OpenData.library import *

config = ConfigParser()
config.read("config/config.ini")


school_subj = {
    "AS": [
        "AAMW",
        "AFRC",
        "AFST",
        "ALAN",
        "AMCS",
        "ANCH",
        "ANEL",
        "ANTH",
        "APOP",
        "ARAB",
        "ARTH",
        "ASAM",
        "ASTR",
        "BCHE",
        "BDS",
        "BENF",
        "BENG",
        "BIBB",
        "BIOL",
        "CHEM",
        "CHIN",
        "CIMS",
        "CLCH",
        "CLST",
        "COGS",
        "COML",
        "CRIM",
        "CRWR",
        "DATA",
        "DEMG",
        "DTCH",
        "DYNM",
        "EALC",
        "ECON",
        "EEUR",
        "ENGL",
        "ENVS",
        "FOLK",
        "FREN",
        "GAFL",
        "GAS",
        "GEOL",
        "GLBS",
        "GREK",
        "GRMN",
        "GSWS",
        "GUJR",
        "HEBR",
        "HIND",
        "HIST",
        "HSOC",
        "HSSC",
        "ICOM",
        "IMPA",
        "INTR",
        "ITAL",
        "JPAN",
        "JWST",
        "KORN",
        "LALS",
        "LATN",
        "LEAD",
        "LGIC",
        "LING",
        "MATH",
        "MCS",
        "MLA",
        "MLYM",
        "MMP",
        "MODM",
        "MTHS",
        "MUSC",
        "NELC",
        "NEUR",
        "ORGC",
        "PERS",
        "PHIL",
        "PHYS",
        "PPE",
        "PROW",
        "PRTG",
        "PSCI",
        "PSYC",
        "PUNJ",
        "QUEC",
        "RELC",
        "RELS",
        "ROML",
        "RUSS",
        "SAST",
        "SCND",
        "SKRT",
        "SLAV",
        "SOCI",
        "SPAN",
        "SPRO",
        "STSC",
        "TAML",
        "TELU",
        "THAR",
        "TURK",
        "URBS",
        "URDU",
        "VIPR",
        "VLST",
        "WRIT",
        "YDSH",
    ],
    "WH": [
        "ACCT",
        "BEPP",
        "FNCE",
        "HCMG",
        "INTS",
        "LGST",
        "LSMP",
        "MGEC",
        "MGMT",
        "MKTG",
        "OIDD",
        "REAL",
        "STAT",
        "WH",
        "WHCP",
    ],
    "MD": [
        "ANAT",
        "BIOE",
        "BIOM",
        "BMB",
        "BMIN",
        "BSTA",
        "CAMB",
        "EPID",
        "GCB",
        "HCIN",
        "HPR",
        "IMUN",
        "MED",
        "MPHY",
        "MTR",
        "NGG",
        "PHRM",
        "PUBH",
        "REG",
    ],
    "FA": ["ARCH", "CPLN", "ENMG", "FNAR", "HSPV", "LARP", "MUSA"],
    "EG": [
        "BE",
        "BIOT",
        "CBE",
        "CIS",
        "CIT",
        "DATS",
        "EAS",
        "ENGR",
        "ENM",
        "ESE",
        "IPD",
        "MEAM",
        "MSE",
        "NANO",
        "NETS",
    ],
    "AN": ["COMM"],
    "DM": ["DADE", "DCOH", "DEND", "DENT", "DOMD", "DORT", "DOSP", "DPED", "DRST"],
    "ED": ["EDUC"],
    "PV": ["INTL", "MSCI", "NSCI"],
    "LW": ["LAW", "LAWM"],
    "SW": ["MSSP", "NPLD", "SWRK"],
    "NU": ["NURS"],
    "VM": ["VBMS", "VCSN", "VCSP", "VISR", "VMED", "VPTH"],
}

"""
def update_school_subj():
    with open('OpenData.txt') as json_file:
        data = json.load(json_file)
        dept = data['departments'] # these are the subjects
        school_subj_map = data['school_subj_map']


        for school in school_data:
            create_instance('schools', school)
            subjects = school_subj_map[school["opendata_abbr"]] # list of the dept/subject abbr in that school
            for subj in subjects:
                subject_data  = {
                    "abbreviation": subj,
                    "name": dept[subj],
                    "visible": True,
                    "schools": school['abbreviation']
                }
                create_instance('subjects',subject_data)
"""


class Command(BaseCommand):
    help = "add subject (see file for data)"

    """
    FROM MODELS
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10,unique=True, primary_key=True)
    visible = models.BooleanField(default=True)
    schools = models.ForeignKey(School,related_name='subjects', on_delete=models.CASCADE, blank=True,null=True)
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--opendata", action="store_true", help="pull from OpenData API"
        )
        parser.add_argument(
            "-l", "--localstore", action="store_true", help="pull from Local Store"
        )

        # parser.add_argument('-p', '--prefix', type=str, help='Define a username prefix')
        # parser.add_argument('-a', '--admin', action='store_true', help='Create an admin account')
        # parser.add_argument('-c', '--courseware', action='store_true', help='Quick add Courseware Support team as Admins')

    def handle(self, *args, **kwargs):
        # courseware = kwargs['courseware']
        opendata = kwargs["opendata"]

        if opendata:
            fails = 0
            domain = config.get("opendata", "domain")
            id = config.get("opendata", "id")
            key = config.get("opendata", "key")
            print(domain, id, key)
            OData = OpenData(base_url=domain, id=id, key=key)
            # saved for special lookups
            OData_lookup = OpenData(base_url=domain, id=id, key=key)
            # saved for special lookups
            OData_lookup = OpenData(base_url=domain, id=id, key=key)
            data = OData.get_available_subj()
            total = len(data)
            print(data)
            # key is the abbr, #value is the name
            for key, value in data.items():
                # check if it exists!
                try:
                    subject = Subject.objects.get(abbreviation=key)
                    print("found subject", subject)
                except:  # it doesnt exist
                    # need to find school first !
                    school_code = OData_lookup.find_school_by_subj(key)
                    # check if the school exists
                    try:
                        school = School.object.get(opendata_abbr=school_code)
                        # we have the school now we can add the subject
                        subject = Subject.objects.create(
                            abbreviation=key, name=value, visible=True, schools=school
                        )
                        print("subject", subject)
                    except:  # the school doesnt exist either
                        logging.getLogger("error_logger").error(
                            "Couldn't add %s b/c couldn't find school %s",
                            key,
                            school_code,
                        )
                        fails += 1
            print("failed %s/%s" % (fails, total))

        else:
            with open("OpenData/OpenData.txt") as json_file:
                data = json.load(json_file)
                # print(data.keys()) =dict_keys(['activity_map', 'departments', 'programs', 'school_subj_map'])
                """
                steps
                1. iterate through school subj mapping and take each school abbr "AS"
                    a. look up "AS" as school object
                    b. iterate list of subjs
                        - look up departments['subj'] to get full name
                    c. create Subject object
                """
                for (school, subjs) in data["school_subj_map"].items():
                    print(school, subjs)
                    try:
                        this_school = School.objects.get(opendata_abbr=school)
                    except:
                        # make this a log
                        logging.getLogger("error_logger").error(
                            "couldnt find school " + school
                        )
                        print("couldnt find school " + school)

                    #
                    print(subjs)
                    for subj in subjs:
                        # need to see if exists
                        if Subject.objects.filter(abbreviation=subj).exists() == False:
                            try:
                                subj_name = data["departments"][subj]
                                Subject.objects.create(
                                    name=subj_name,
                                    abbreviation=subj,
                                    visible=True,
                                    schools=this_school,
                                )
                            except:
                                logging.getLogger("error_logger").error(
                                    "couldnt find subj in departments: " + subj
                                )
                                print("couldnt find subj in departments: " + subj)
                                Subject.objects.create(
                                    name=subj + "-- FIX ME",
                                    abbreviation=subj,
                                    visible=True,
                                    schools=this_school,
                                )
                        else:
                            print("subject already exists: " + subj)
