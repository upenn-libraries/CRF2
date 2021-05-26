# doc https://esb.isc-seo.upenn.edu/8091/
# https://esb.isc-seo.upenn.edu/8091/open_data/course_info/


# https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search_parameters/


import json
import pprint as pp
import random
import re
import time
from configparser import ConfigParser

import requests
from loading_with_api import *

# here are most of the basic API requests that should support the CRF

config = ConfigParser()
config.read("../config/config.ini")


domain = config.get("opendata", "domain")
id = config.get("opendata", "id")
key = config.get("opendata", "key")
headers = {"Authorization-Bearer": id, "Authorization-Token": key}


# I WISH I HAD KNOWN ABOUT THIS https://github.com/pennlabs/penn-sdk-python


# SCHOOLS
# ['DM', 'ED', 'EG', 'VM', 'AN', 'FA', 'AS', 'WH', 'MD', 'PV', 'SW', 'LW', 'NU']


#######################################################################
## The Data below is not exhaustive and there is probably more
## data than
#######################################################################
school_data = [
    {
        "abbreviation": "AN",
        "name": "Annenberg School For Communication",
        "visibility": True,
        "opendata_abbr": "AN",
    },
    {
        "abbreviation": "SAS",
        "name": "Arts & Sciences",
        "visibility": True,
        "opendata_abbr": "AS",
    },
    {
        "abbreviation": "DM",
        "name": "Dental Medicine",
        "visibility": True,
        "opendata_abbr": "DM",
    },
    {
        "abbreviation": "GSE",
        "name": "Graduate School Of Education",
        "visibility": False,
        "opendata_abbr": "ED",
    },
    {
        "abbreviation": "SEAS",
        "name": "Engineering",
        "visibility": True,
        "opendata_abbr": "EG",
    },
    {"abbreviation": "FA", "name": "Design", "visibility": True, "opendata_abbr": "FA"},
    {"abbreviation": "LW", "name": "Law", "visibility": True, "opendata_abbr": "LW"},
    {
        "abbreviation": "PSOM",
        "name": "Perelman School Of Medicine",
        "visibility": True,
        "opendata_abbr": "MD",
    },
    {
        "abbreviation": "NURS",
        "name": "Nursing",
        "visibility": True,
        "opendata_abbr": "NU",
    },
    {
        "abbreviation": "PC",
        "name": "Provost Center",
        "visibility": True,
        "opendata_abbr": "PV",
    },
    {
        "abbreviation": "SP2",
        "name": "Social Policy & Practice",
        "visibility": True,
        "opendata_abbr": "SW",
    },
    {
        "abbreviation": "VET",
        "name": "Veterinary Medicine",
        "visibility": True,
        "opendata_abbr": "VM",
    },
    {
        "abbreviation": "WH",
        "name": "Wharton",
        "visibility": True,
        "opendata_abbr": "WH",
    },
    {
        "abbreviation": "XX",
        "name": "Special Programs",
        "visibility": True,
        "opendata_abbr": "XX",
    },
]
# {"abbreviation": "SS", "name":"Summer Sessions", "visibility": True, "opendata_abbr":""},
# Special Programs should include the "Programs" defined below or other general mislabeled!
opendata_crf_school_mappings = {
    "DM": "DM",
    "ED": "GSE",
    "EG": "SEAS",
    "VM": "VET",
    "AN": "AN",
    "FA": "FA",
    "AS": "SAS",
    "WH": "WH",
    "MD": "PSOM",
    "PV": "PC",
    "SW": "SP2",
    "LW": "LW",
    "NU": "NURS",
}

programs = {
    "BFS": "Ben Franklin Seminars",
    "CGS": "College of Liberal & Professional Studies",
    "CRS": "Critical Writing Seminars",
    "FORB": "Freshman-Friendly courses",
    "MFS": "Freshman Seminars",
    "MPG": "Penn Global Seminars",
    "MSL": "Academically Based Community Service Courses",
    "ONL": "Penn LPS Online",
    "PLC": "Penn Language Center",
    "SS": "Summer Sessions I & II",
    "WPWP": "Wharton Programs for Working Professionals",
}


# mapping of two char School code to subjects
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

########################################################################################
## there is a bit of an issue where ther is not a mapping of schools to subjects ...  ##
## here is a good start. the rest will have to be done ad hoc                         ##
#########################################################################################


def update_school_subj():
    with open("OpenData.txt") as json_file:
        data = json.load(json_file)
        dept = data["departments"]  # these are the subjects
        school_subj_map = data["school_subj_map"]

        for school in school_data:
            create_instance("schools", school)
            subjects = school_subj_map[
                school["opendata_abbr"]
            ]  # list of the dept/subject abbr in that school
            for subj in subjects:
                subject_data = {
                    "abbreviation": subj,
                    "name": dept[subj],
                    "visible": True,
                    "schools": school["abbreviation"],
                }
                create_instance("subjects", subject_data)


def find_school(subject):
    for school in school_subj:
        if subject in school_subj[school]:
            return opendata_crf_school_mappings[school]
    return None
    # this should be logged
    print("Couldnt find %s in the current subject lists" % (subject))


def check_activity(abbr):
    activity_map = {
        "LEC": "Lecture",
        "REC": "Recitation",
        "LAB": "Laboratory",
        "IND": "Independent Study",
        "SEM": "Seminar",
        "SRT": "Senior Thesis",
        "STU": "Studio",
        "CLN": "Clinic",
        "PRC": "SCUE Preceptorial",
        "PRO": "NSO Proseminar",
    }
    if abbr in [*activity_map]:
        return True
    else:
        return False


def get_courses():

    # create OpenData API wrapper object
    OpenData = library.OpenData()
    terms = OpenData.get_available_terms()

    for term in terms:
        next = True
        while next:
            #

            for course in data:
                pp.pprint(course)

                ###############################################################################
                #### we need to have some way to check if the associated data already exists ##
                ###############################################################################

                # CHECK ACTIVITY
                if check_activity(course["activity"]):
                    activity = course["activity"]
                else:
                    activity = "UNK"

                # CHECK SCHOOLS - happend in the find school
                # we may need the school if we have to create the subject
                course_school = find_school(course["course_department"])
                if course_school == None:
                    OpenData.find_school_by_subj(course["course_department"])
                    school_data = {
                        "abbreviation": course_school,
                        "name": course["department_description"],
                        "visible": "true",
                        "opendata_abbr": course_school[:2],
                    }
                    # add it to the file

                # CHECK SUBJECTS
                subject = course["course_department"]
                if check_instance("subjects", subject):
                    pass
                else:
                    # create subject
                    subject_data = {
                        "abbreviation": subject,
                        "name": course["department_description"],
                        "visible": "true",
                        "schools": course_school,
                    }
                    create_instance("subject", subject_data)

                    # add it to the file.

                # CHECK INSTRUCTORS instructors': [{'name': 'Elizabeth Shank', 'penn_id': '10124627', 'section_id': 'AAMW520401', 'term': '2019C'}]
                for instructor in course["instructors"]:
                    if check_instructor(instructor["penn_id"]):
                        pass
                    else:
                        create_instructor(instructor["penn_id"])
                # check_instructors(data['instructors'])

                course_school = find_school(course["course_department"])
                if course[
                    "crosslist_primary"
                ]:  # if this is true then the current is the primary course
                    primary_subj = course["crosslist_primary"][:-6]
                else:
                    # the listed course_subject is the primary one
                    primary_subj = course["course_department"]

                course_data = {
                    "course_code": "x",
                    "instructors": ["mfhodges"],
                    "course_schools": [course_school],
                    "course_subject": course["course_department"],
                    "course_term": term[-1],
                    "course_activity": course["activity"],
                    "course_number": course["course_number"],
                    "course_section": course["section_number"],
                    "course_name": course["course_title"],
                    "year": term[:-1],
                    "requested": False,
                    "course_primary_subject": primary_subj,
                }

                if not course_is_unique(course_data):
                    # we have NOT created this course yet so lets create it

                    # have the create_instance be a try and if it doesnt work write it down
                    create_instance("courses", course_data)
                    if course["crosslistings"]:
                        print(course["crosslistings"])
                        print("MAIN COURSE")
                        pp.pprint(course_data, indent=2)
                        input("wait a minute")

                        crosslist_codes = []
                        for crosslist in course["crosslistings"]:
                            # make the course - we only need to change a few attributes ...
                            course_data["course_number"] = crosslist["course_id"]
                            course_data["course_section"] = crosslist["section_id"]
                            course_data["course_subject"] = crosslist["subject"]
                            course_code = (
                                course_data["course_subject"]
                                + course_data["course_section"]
                                + course_data["course_number"]
                                + term
                            )
                            crosslist_codes.append(course_code)
                            print("CROSSLISTED COURSE")

                            pp.pprint(course_data, indent=2)
                            if not course_is_unique(course_data):
                                create_instance("courses", course_data)
                        # crosslist them
                        # FIX THIS
                        if crosslist_codes:
                            primary = course["crosslist_primary"] + term
                            cross_list(primary, crosslist_codes)
                else:  # course already exists
                    pass
                    # print("course already exists")
                print(
                    "~~~~~~~~~~~~~~~~~~~~~  NEXT COURSE   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                )

            #

    # need to have something that checks about throttling and if its mad have it wait 5 min..


def main():
    get_courses()


if __name__ == "__main__":
    main()


# schools = {'AS': ['AAMW', 'AFRC', 'AFST', 'ALAN', 'AMCS', 'ANCH', 'ANEL', 'ANTH', 'APOP', 'ARAB', 'ARTH', 'ASAM', 'ASTR', 'BCHE', 'BDS', 'BENF', 'BENG', 'BIBB', 'BIOL', 'CHEM', 'CHIN', 'CIMS', 'CLCH', 'CLST', 'COGS', 'COML', 'CRIM', 'CRWR', 'DATA', 'DEMG', 'DTCH', 'DYNM', 'EALC', 'ECON', 'EEUR', 'ENGL', 'ENVS', 'FOLK', 'FREN', 'GAFL', 'GAS', 'GEOL', 'GLBS', 'GREK', 'GRMN', 'GSWS', 'GUJR', 'HEBR', 'HIND', 'HIST', 'HSOC', 'HSSC', 'ICOM', 'IMPA', 'INTR', 'ITAL', 'JPAN', 'JWST', 'KORN', 'LALS', 'LATN', 'LEAD', 'LGIC', 'LING', 'MATH', 'MCS', 'MLA', 'MLYM', 'MMP', 'MODM', 'MTHS', 'MUSC', 'NELC', 'NEUR', 'ORGC', 'PERS', 'PHIL', 'PHYS', 'PPE', 'PROW', 'PRTG', 'PSCI', 'PSYC', 'PUNJ', 'QUEC', 'RELC', 'RELS', 'ROML', 'RUSS', 'SAST', 'SCND', 'SKRT', 'SLAV', 'SOCI', 'SPAN', 'SPRO', 'STSC', 'TAML', 'TELU', 'THAR', 'TURK', 'URBS', 'URDU', 'VIPR', 'VLST', 'WRIT', 'YDSH'], 'WH': ['ACCT', 'BEPP', 'FNCE', 'HCMG', 'INTS', 'LGST', 'LSMP', 'MGEC', 'MGMT', 'MKTG', 'OIDD', 'REAL', 'STAT', 'WH', 'WHCP'], 'MD': ['ANAT', 'BIOE', 'BIOM', 'BMB', 'BMIN', 'BSTA', 'CAMB', 'EPID', 'GCB', 'HCIN', 'HPR', 'IMUN', 'MED', 'MPHY', 'MTR', 'NGG', 'PHRM', 'PUBH', 'REG'], 'FA': ['ARCH', 'CPLN', 'ENMG', 'FNAR', 'HSPV', 'LARP', 'MUSA'], 'EG': ['BE', 'BIOT', 'CBE', 'CIS', 'CIT', 'DATS', 'EAS', 'ENGR', 'ENM', 'ESE', 'IPD', 'MEAM', 'MSE', 'NANO', 'NETS'], 'AN': ['COMM'], 'DM': ['DADE', 'DCOH', 'DEND', 'DENT', 'DOMD', 'DORT', 'DOSP', 'DPED', 'DRST'], 'ED': ['EDUC'], 'PV': ['INTL', 'MSCI', 'NSCI'], 'LW': ['LAW', 'LAWM'], 'SW': ['MSSP', 'NPLD', 'SWRK'], 'NU': ['NURS'], 'VM': ['VBMS', 'VCSN', 'VCSP', 'VISR', 'VMED', 'VPTH']}

## just call create_instance!


"""
'activity': 'LEC',
 'activity_description': 'Lecture',
 'corequisite_activity': '',
 'corequisite_activity_description': '',
 'course_department': 'ACCT',
 'course_description': 'This course is an introduction to the basic concepts '
                       'and standards underlying financial accounting systems. '
                       'Several important concepts will be studied in detail, '
                       'including: revenue recognition, inventory, long-lived '
                       'assets, present value, and long term liabilities. The '
                       'course emphasizes the construction of the basic '
                       'financial accounting statements - the income '
                       'statement, balance sheet, and cash flow statement - as '
                       'well as their interpretation.',
 'course_description_url': '',
 'course_meeting_message': '',
 'course_notes': '',
 'course_notes_message': '',
 'course_number': '101',
 'course_status': 'C',
 'course_status_normalized': 'Closed',
 'course_status_reason_code': '',
 'course_terms_offered': 'One-term course offered either term',
 'course_title': 'Accounting and Financial Reporting',
 'credit_and_grade_type': '1 CU',
 'credit_connector': 'F',
 'credit_type': 'CU',
 'credits': '1 CU',
 'crosslist_primary': '',
 'crosslistings': [],
 'department_description': 'Accounting',
 'department_url': 'http://accounting.wharton.upenn.edu',
 'end_date': '2019-07-03T04:00:00Z',
 'first_meeting_days': 'MTWR02:00 PMJMHHG60',
 'fulfills_college_requirements': [],
 'grade_type': '',
 'important_notes': ['Auditors Need Permission'],
 'instructors': [{'name': 'Jung Min Kim',
                  'penn_id': '79944691',
                  'section_id': 'ACCT101910',
                  'term': '2019B'}],
 'is_cancelled': False,
 'is_closed': True,
 'is_crosslist_primary': False,
 'is_not_scheduled': False,
 'is_special_session': False,
 'labs': [],
 'lectures': [],
 'max_enrollment': '90',
 'max_enrollment_crosslist': '90',
 'maximum_credit': '1',
 'meetings': [{'building_code': '',
               'building_name': '',
               'end_hour_24': 16,
               'end_minutes': 0,
               'end_time': '04:00 PM',
               'end_time_24': 16.0,
               'meeting_days': 'MTWR',
               'room_number': '',
               'section_id': 'ACCT101910',
               'section_id_normalized': 'ACCT-101-910',
               'start_hour_24': 14,
               'start_minutes': 0,
               'start_time': '02:00 PM',
               'start_time_24': 14.0,
               'term': '2019B'}],
 'minimum_credit': '1',
 'prerequisite_notes': [],
 'primary_instructor': '',
 'recitations': [],
 'requirements': [{'argument': '',
                   'registration_control_code': 'PAU',
                   'requirement_description': 'Auditors Need Permission',
                   'section_id': 'ACCT101910',
                   'term': '2019B',
                   'value': '',
                   'value_normalized': ''}],
 'requirements_title': 'Associated Courses',
 'section_id': 'ACCT101910',
 'section_id_normalized': 'ACCT-101-910',
 'section_number': '910',
 'section_title': 'Acct & Financial Report',
 'start_date': '2019-05-28T04:00:00Z',
 'syllabus_url': '',
 'term': '2019B',
 'term_normalized': 'Summer 2019',
 'term_session': '1',
 'third_party_links': []}



"""


"""

###################################
######## LOCAL DATA STORE #########
###################################
#data = {}
#data['activity_map'] = activity_map
#data['departments']=departments
#data['programs']=programs
#data['school_subj_map']= {"AS": ["AAMW", "AFRC", "AFST", "ALAN", "AMCS", ...
#with open("OpenData.txt",'w') as outfile:
#    json.dump(data,outfile)


Data provided by API stored in file defined above retreived from the search parameters
###################################
########## ACTIVITY MAP ###########
###################################
{
 'CLN': 'Clinic',
 'IND': 'Independent Study',
 'LAB': 'Laboratory',
 'LEC': 'Lecture',
 'ONL': 'Online Course',
 'PRC': 'SCUE Preceptorial',
 'PRO': 'NSO Proseminar',
 'REC': 'Recitation',
 'SEM': 'Seminar',
 'SRT': 'Senior Thesis',
 'STU': 'Studio'
 }


###################################
######## AVAILABLE TERMS ##########
###################################

{'2019B': 'Summer 2019', '2019C': 'Fall 2019'}
NOTE: are not current term ..
###################################
########## DEPARTMENTS ############
###################################
{'AAMW': 'Art & Arch of Med. World',
 'ACCT': 'Accounting',
 'AFRC': 'Africana Studies',
 'AFST': 'African Studies Program',
 'ALAN': 'Asian Languages',
 'AMCS': 'Applied Math & Computatnl Sci.',
 'ANAT': 'Anatomy',
 'ANCH': 'Ancient History',
 'ANEL': 'Ancient Near East Languages',
 'ANTH': 'Anthropology',
 'APOP': 'Applied Positive Psychology',
 'ARAB': 'Arabic',
 'ARCH': 'Architecture',
 'ARTH': 'Art History',
 'ASAM': 'Asian American Studies',
 'ASTR': 'Astronomy',
 'BCHE': 'Biochemistry (Undergrads)',
 'BDS': 'Behavioral & Decision Sciences',
 'BE': 'Bioengineering',
 'BENF': 'Benjamin Franklin Seminars',
 'BENG': 'Bengali',
 'BEPP': 'Business Econ & Pub Policy',
 'BIBB': 'Biological Basis of Behavior',
 'BIOE': 'Bioethics',
 'BIOL': 'Biology',
 'BIOM': 'Biomedical Studies',
 'BIOT': 'Biotechnology',
 'BMB': 'Biochemistry & Molecular Biophy',
 'BMIN': 'Biomedical Informatics',
 'BSTA': 'Biostatistics',
 'CAMB': 'Cell and Molecular Biology',
 'CBE': 'Chemical & Biomolecular Engr',
 'CHEM': 'Chemistry',
 'CHIN': 'Chinese',
 'CIMS': 'Cinema and Media Studies',
 'CIS': 'Computer and Information Sci',
 'CIT': 'Computer and Information Tech',
 'CLCH': 'Climate Change',
 'CLST': 'Classical Studies',
 'COGS': 'Cognitive Science',
 'COML': 'Comparative Literature',
 'COMM': 'Communications',
 'CPLN': 'City Planning',
 'CRIM': 'Criminology',
 'CRWR': 'Creative Writing',
 'DADE': 'Core Curriculum Basic Science',
 'DATA': 'Data Analytics',
 'DATS': 'Data Science',
 'DCOH': 'Community Oral Health',
 'DEMG': 'Demography',
 'DEND': 'Endodontics',
 'DENT': 'Dental',
 'DOMD': 'Oral Medicine',
 'DORT': 'Orthodontics',
 'DOSP': 'Oral Surgery and Pharmacology',
 'DPED': 'Pediatric Dentistry',
 'DRST': 'Restorative Dentistry',
 'DTCH': 'Dutch',
 'DYNM': 'Organizational Dynamics',
 'EALC': 'East Asian Languages & Civilztn',
 'EAS': 'Engineering & Applied Science',
 'ECON': 'Economics',
 'EDUC': 'Education',
 'EEUR': 'East European',
 'ENGL': 'English',
 'ENGR': 'Engineering',
 'ENM': 'Engineering Mathematics',
 'ENMG': 'Energy Management & Policy',
 'ENVS': 'Environmental Studies',
 'EPID': 'Epidemiology',
 'ESE': 'Electric & Systems Engineering',
 'FNAR': 'Fine Arts',
 'FNCE': 'Finance',
 'FOLK': 'Folklore',
 'FREN': 'French',
 'GAFL': 'Government Administration',
 'GAS': 'Graduate Arts & Sciences',
 'GCB': 'Genomics & Comp. Biology',
 'GEOL': 'Geology',
 'GLBS': 'Global Studies',
 'GREK': 'Greek',
 'GRMN': 'Germanic Languages',
 'GSWS': "Gender,Sexuality&Women's Stdys",
 'GUJR': 'Gujarati',
 'HCIN': 'Health Care Innovation',
 'HCMG': 'Health Care Management',
 'HEBR': 'Hebrew',
 'HIND': 'Hindi',
 'HIST': 'History',
 'HPR': 'Health Policy Research',
 'HSOC': 'Health & Societies',
 'HSPV': 'Historic Preservation',
 'HSSC': 'History & Sociology of Science',
 'ICOM': 'Intercultural Communication',
 'IMPA': 'International Mpa',
 'IMUN': 'Immunology',
 'INTL': 'International Programs',
 'INTR': 'International Relations',
 'INTS': 'International Studies',
 'IPD': 'Integrated Product Design',
 'ITAL': 'Italian',
 'JPAN': 'Japanese',
 'JWST': 'Jewish Studies Program',
 'KORN': 'Korean',
 'LALS': 'Latin American & Latino Studies',
 'LARP': 'Landscape Arch & Regional Plan',
 'LATN': 'Latin',
 'LAW': 'Law',
 'LAWM': 'Master in Law',
 'LEAD': 'Leadership and Communication',
 'LGIC': 'Logic, Information and Comp.',
 'LGST': 'Legal Studies & Business Ethics',
 'LING': 'Linguistics',
 'LSMP': 'Life Sciences Management Prog',
 'MATH': 'Mathematics',
 'MCS': 'Master of Chemical Sciences',
 'MEAM': 'Mech Engr and Applied Mech',
 'MED': 'Medical',
 'MGEC': 'Management of Economics',
 'MGMT': 'Management',
 'MKTG': 'Marketing',
 'MLA': 'Master of Liberal Arts Program',
 'MLYM': 'Malayalam',
 'MMP': 'Master of Medical Physics',
 'MODM': 'Modern Middle East Studies',
 'MPHY': 'Medical Physics',
 'MSCI': 'Military Science',
 'MSE': 'Materials Science and Engineer',
 'MSSP': 'Social Policy',
 'MTHS': 'Mathematical Sciences',
 'MTR': 'Mstr Sci Transltl Research',
 'MUSA': 'Master of Urban Spatial Analyt',
 'MUSC': 'Music',
 'NANO': 'Nanotechnology',
 'NELC': 'Near Eastern Languages & Civlzt',
 'NETS': 'Networked and Social Systems',
 'NEUR': 'Neuroscience',
 'NGG': 'Neuroscience',
 'NPLD': 'Nonprofit Leadership',
 'NSCI': 'Naval Science',
 'NURS': 'Nursing',
 'OIDD': 'Operations Info Decisions',
 'ORGC': 'Organizational Anthropology',
 'PERS': 'Persian',
 'PHIL': 'Philosophy',
 'PHRM': 'Pharmacology',
 'PHYS': 'Physics',
 'PPE': 'Philosophy, Politics, Economics',
 'PROW': 'Professional Writing',
 'PRTG': 'Portuguese',
 'PSCI': 'Political Science',
 'PSYC': 'Psychology',
 'PUBH': 'Public Health Studies',
 'PUNJ': 'Punjabi',
 'QUEC': 'Quechua',
 'REAL': 'Real Estate',
 'REG': 'Regulation',
 'RELC': 'Religion and Culture',
 'RELS': 'Religious Studies',
 'ROML': 'Romance Languages',
 'RUSS': 'Russian',
 'SAST': 'South Asia Studies',
 'SCND': 'Scandinavian',
 'SKRT': 'Sanskrit',
 'SLAV': 'Slavic',
 'SOCI': 'Sociology',
 'SPAN': 'Spanish',
 'SPRO': 'Scientific Process',
 'STAT': 'Statistics',
 'STSC': 'Science, Technology & Society',
 'SWRK': 'Social Work',
 'TAML': 'Tamil',
 'TELU': 'Telugu',
 'THAR': 'Theatre Arts',
 'TURK': 'Turkish',
 'URBS': 'Urban Studies',
 'URDU': 'Urdu',
 'VBMS': 'Veterinary & Biomedical Science',
 'VCSN': 'Clinical Studies - Nbc Elect',
 'VCSP': 'Clinical Studies - Phila Elect',
 'VIPR': 'Viper',
 'VISR': 'Vet School Ind Study & Research',
 'VLST': 'Visual Studies',
 'VMED': 'Csp/Csn Medicine Courses',
 'VPTH': 'Pathobiology',
 'WH': 'Wharton Undergraduate',
 'WHCP': 'Wharton Communication Pgm',
 'WRIT': 'Writing Program',
 'YDSH': 'Yiddish'}

###################################
###########  PROGRAMS #############
###################################
{'BFS': 'Ben Franklin Seminars',
 'CGS': 'College of Liberal & Professional Studies',
 'CRS': 'Critical Writing Seminars',
 'FORB': 'Freshman-Friendly courses',
 'MFS': 'Freshman Seminars',
 'MPG': 'Penn Global Seminars',
 'MSL': 'Academically Based Community Service Courses',
 'ONL': 'Penn LPS Online',
 'PLC': 'Penn Language Center',
 'SS': 'Summer Sessions I & II',
 'WPWP': 'Wharton Programs for Working Professionals'
 }


"""
