# https://esb.isc-seo.upenn.edu/8091/open_data/course_info/


# https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search_parameters/


import json
import pprint as pp
import re
import time
from configparser import ConfigParser

import requests

# here are most of the basic API requests that should support the CRF

config = ConfigParser()
config.read("../config/config.ini")
domain = config.get("opendata", "domain")
id = config.get("opendata", "id")

key = config.get("opendata", "key")
headers = {"Authorization-Bearer": id, "Authorization-Token": key}

# course_info/ACCT/
"""
url = domain + 'course_section_search_parameters/'
print(url)
response = requests.get(url,headers=headers)
r_json = response.json()
r_json = r_json['result_data'][0]
pp.pprint(r_json)
pp.pprint(r_json['activity_map'])

pp.pprint(r_json['available_terms_map'])

pp.pprint(r_json['departments_map'])
pp.pprint(r_json['program_map'])

url = domain + 'course_section_search'
print(url)
response = requests.get(url,headers=headers,params={'course_id':'ENGL'})
print(response.links,response.url)
pp.pprint(response.headers)
r_json = response.json()
#pp.pprint(r_json)
"""


def main():
    schools = {}
    with open("OpenData.txt") as json_file:
        data = json.load(json_file)
        print("data['departments']", len(data["departments"].keys()))
        # for dept in data['departments']:
        """
            print('Dept: ' + dept)
            url = '%scourse_info/%s/' % (domain,dept) # gives u the course code
            params = {'number_of_results_per_page':'5'}
            response = requests.get(url,headers=headers,params=params)
            try:
                school_code = response.json()['result_data'][0]["school_code"]
            except IndexError:
                print(response.json()['result_data'])
                print("...sleeping 60 seconds...")
                time.sleep(60)

            #      pp.pprint(school_code)
            if school_code in schools.keys():
                #just add the dept to its list
                schools[school_code].append(dept)
            else:
                #create it
                print("new school: ", school_code)
                schools[school_code] = []
                schools[school_code].append(dept)
            #print(schools[school_code])
        """

    print(data["departments"].keys())

    schools = {
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
    subj_list = []
    for school in schools:
        subj_list += schools[school]
    print(data["departments"].keys())
    print(subj_list)

    for x in data["departments"].keys():
        if x not in subj_list:
            print(x, " not in subj list")

    num_dept = len(subj_list)
    print("num_dept", num_dept)
    # pp.pprint(schools.values())


url = domain + "course_section_search"
params = {
    "term": "2019B",
    "course_id": "CIS",
    "course_level_at_or_above": "200",
    "page_number": 2,
    "number_of_results_per_page": "100",
}
response = requests.get(url, headers=headers, params=params)
pp.pprint(response.json())
print(response.links, response.url)


"""
# contact: opendata-help@lists.upenn.edu
  "service_meta" : {
    "current_page_number" : 1,
    "error_text" : "",
    "last_updated" : "",
    "next_page_number" : 2,
    "number_of_pages" : -1,
    "previous_page_number" : 1,
    "results_per_page" : 30
  }
 there is no pagination!
"""


"""
#data = {}
#data['activity_map'] = activity_map
#data['departments']=departments
#data['programs']=programs
#pp.pprint(data)
#with open("OpenData.txt",'w') as outfile:
#    json.dump(data,outfile)


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
 'WPWP': 'Wharton Programs for Working Professionals'}


"""
