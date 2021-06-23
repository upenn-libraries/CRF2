import json
import logging
from configparser import ConfigParser

from django.core.management.base import BaseCommand

from course.models import School, Subject
from OpenData.library import OpenData

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
            subjects = school_subj_map[school["opendata_abbr"]] # list of the
            dept/subject abbr in that school
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
    schools = models.ForeignKey(School,related_name='subjects',
    on_delete=models.CASCADE, blank=True,null=True)
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--opendata",
            action="store_true",
            help="Pull subjects from the OpenData API",
        )

    def handle(self, *args, **kwargs):
        print(") Adding subjects...")

        open_data = kwargs["opendata"]

        if open_data:
            fails = 0
            domain = config.get("opendata", "domain")
            open_data_id = config.get("opendata", "id")
            key = config.get("opendata", "key")
            open_data_connection = OpenData(base_url=domain, id=open_data_id, key=key)
            subjects = open_data_connection.get_available_subj()
            subjects_total = len(subjects)
            schools_not_found = list()
            subjects_not_found = list()

            try:
                for index, value in enumerate(subjects.items()):
                    abbreviation, subject_name = value
                    message = f"- ({index}/{subjects_total})"

                    if not Subject.objects.filter(abbreviation=abbreviation).exists():
                        try:
                            school_code = open_data_connection.find_school_by_subj(
                                abbreviation
                            )
                            school_name = School.objects.get(opendata_abbr=school_code)
                            subject = Subject.objects.create(
                                abbreviation=abbreviation,
                                name=subject_name,
                                visible=True,
                                schools=school_name,
                            )
                            print(f"{message} Added {subject_name} ({abbreviation}).")
                        except Exception:
                            schools_not_found.append(school_code)
                            message = (
                                f"{message} ERROR: Failed to add {subject_name} ({abbreviation}) [school code not"
                                f" found: {school_code}]."
                            )
                            logging.getLogger("error_logger").error(message)
                            print(message)
                            fails += 1
                    else:
                        print(f"{message} Subject {subject_name} already exists.")

                if fails > 0 or len(schools_not_found) > 0:
                    print("SUMMARY")
                    if fails > 0:
                        print(
                            f"- Failed to find {fails} out of {subjects_total} total subjects."
                        )
                    if len(schools_not_found) > 0:
                        print("- Schools not found:")
                        for school in schools_not_found:
                            print(f"\t{school}")

                print("FINISHED")
            except Exception:
                print(subjects)
        else:
            with open("OpenData/OpenData.json") as json_file:
                subjects = json.load(json_file)

                for school_name, subjects_list in subjects["school_subj_map"].items():
                    try:
                        school = School.objects.get(opendata_abbr=school_name)
                    except Exception:
                        logging.getLogger("error_logger").error(
                            f"Failed to find {school_name}"
                        )

                    for index, subject in enumerate(subjects_list):
                        message = f"- ({index}/{len(subjects_total)})"

                        if not Subject.objects.filter(abbreviation=subject).exists():
                            try:
                                subject_name = subjects["departments"][subject]
                                Subject.objects.create(
                                    name=subject_name,
                                    abbreviation=subject,
                                    visible=True,
                                    schools=school,
                                )
                                print(
                                    f"{message} Added {subject_name} ({abbreviation})."
                                )
                            except Exception:
                                schools_not_found.append(school_code)
                                message = f"{message} ERROR: Failed to find subject name for {subject} in departments."
                                logging.getLogger("error_logger").error(message)
                                print(message)

                                Subject.objects.create(
                                    name=subject + "-- FIX ME",
                                    abbreviation=subject,
                                    visible=True,
                                    schools=school,
                                )
                                print(
                                    f"{message} Added {subject} marked with 'FIX ME'."
                                )
                        else:
                            print(f"{message} Subject {subject} already exists.")

            print("FINISHED")
