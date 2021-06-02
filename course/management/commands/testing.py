# https://esb.isc-seo.upenn.edu/8091/open_data/course_info/
# https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search_parameters/
import csv
import sys
from configparser import ConfigParser

from course.models import Course
from OpenData.library import OpenData

config = ConfigParser()
config.read("config/config.ini")


def find_crosslistings(year_term):
    domain = config.get("opendata", "domain")
    id = config.get("opendata", "id2")
    key = config.get("opendata", "key2")
    print(domain, id, key)
    OData = OpenData(base_url=domain, id=id, key=key)

    data = OData.get_courses_by_term(year_term)
    print("data", data)
    page = 1
    with open("crosslisting_fix.csv", mode="w") as crosslisting_fix:
        crosslisting_fix = csv.writer(crosslisting_fix, delimiter=",", quotechar='"')

        while data is not None:
            print("\n\tSTARTING PAGE : ", page, "\n")
            if data == "ERROR":
                print("ERROR")
                sys.exit()
            if isinstance(data, dict):
                # sometimes the data passed back can be a single course and in
                # that case it should be put in a list
                data = [data]
            for datum in data:
                # we want to find when the cross list has diff course number
                # print("datum",datum)
                datum["section_id"] = datum["section_id"].replace(" ", "")
                datum["crosslist_primary"] = datum["crosslist_primary"].replace(" ", "")
                if (
                    datum["section_id"] != datum["crosslist_primary"]
                    and datum["crosslist_primary"] != ""
                ):
                    number1 = datum["section_id"][-6:][:3]
                    number2 = datum["crosslist_primary"][-6:][:3]
                    if number2 != number1:
                        print(datum["section_id"], datum["crosslist_primary"])
                        crosslisting_fix.writerow(
                            [datum["section_id"], datum["crosslist_primary"]]
                        )

            page += 1
            # end of for loop
            # data =None
            data = OData.next_page()


# from course.management.commands.testing import *


# find_crosslistings('2019C')


def fix_crosslistings():
    with open("crosslisting_fix.csv", newline="") as csvfile:
        cx = csv.reader(csvfile, delimiter=",")
        with open("crosslisting_check.csv", mode="w") as check:
            check = csv.writer(check, delimiter=",", quotechar='"')
            for row in cx:
                course = row[0] + "2019C"
                primary = row[1] + "2019C"
                # print(course,primary)
                try:
                    crf_course = Course.objects.get(course_code=course)
                except:
                    crf_course = None
                try:
                    crf_primary = Course.objects.get(course_code=primary)
                except:
                    crf_primary = None

                if crf_course and crf_primary:  # check if either exist
                    crf_course.primary_crosslist = primary

                    if (
                        crf_course.requested or crf_primary.requested
                    ):  # check if either have been requested
                        check.writerow(["needs_review", course, primary])
                    elif not crf_course.requested and not crf_primary.requested:  #
                        # this case we can remediate
                        print("adding", course, primary)
                        crf_course.crosslisted.add(
                            crf_primary
                        )  # symmetrical so dont need to do it the other way
                        check.writerow(["added_cx", course, primary])
                    crf_course.save()
                else:  # one or both dont exist.
                    if crf_course:
                        crf_course.crosslist_primary = crf_primary
                        crf_course.save()
                        print(primary, " doesnt exits")
                    elif crf_primary:
                        print(course, " doesnt exits")
                    else:
                        check.writerow(["neither exist", course, primary])


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
