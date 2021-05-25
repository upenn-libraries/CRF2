from library import *
from configparser import ConfigParser


config = ConfigParser()
config.read("../config/config.ini")

domain = config.get("opendata", "domain")
id = config.get("opendata", "id")
key = config.get("opendata", "key")
headers = {"Authorization-Bearer": id, "Authorization-Token": key}


#################################
##### a lil testing for the #####
##### Open Data API wrapper #####
#################################
# print(">> ")

OpenData = OpenData(domain, id, key)


print(">>  OpenData.get_available_terms()")
print(OpenData.get_available_terms())
input("Press Enter to continue...\n")

print(">> OpenData.call_api(result_data=True)")
OpenData.set_uri("course_section_search")
OpenData.add_param("course_id", "MATH")
OpenData.add_param("term", "2019C")
print([x["section_id"] for x in OpenData.call_api(only_data=True)])
while OpenData.next_page() != None:
    print(
        [(x["instructors"], x["section_id"]) for x in OpenData.call_api(only_data=True)]
    )
    OpenData.next_page()
input("Press Enter to continue...\n")


"""
print(">> OpenData.call_api(result_data=False)")
print(OpenData.call_api(result_data=False))
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

#print(">> OpenData.get_courses_by_term(term1)")
OpenData.clear_settings()
terms = OpenData.get_available_terms()
term1 = terms[0]
OpenData.clear_settings()
print(">> OpenData.get_courses_by_term(term1)")
print(OpenData.get_courses_by_term(term1))
input("Press Enter to continue...\n")
"""


# OpenData.set_uri('directory_person_details/89450759')
# print(OpenData.call_api())
# input("Press Enter to continue...\n")
