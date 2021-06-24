import json
import re
import time
from configparser import ConfigParser

import requests

"""
config = ConfigParser()
config.read('../config/config.ini')

domain = config.get('opendata', 'domain')
id = config.get('opendata', 'id')
key = config.get('opendata', 'key')
headers = {
    'Authorization-Bearer' : id,
    'Authorization-Token':key
}
"""


class OpenData(object):
    def __init__(self, base_url, id, key):
        # sets the information in the headers
        self.headers = {"Authorization-Bearer": id, "Authorization-Token": key}
        self.base_url = base_url
        self.uri = ""
        self.params = {
            "number_of_results_per_page": 30,
            "page_number": 1,
        }

    def clear_settings(self):
        self.uri = ""
        self.params = {
            "number_of_results_per_page": 30,
            "page_number": 1,
        }

    def set_uri(self, new_uri):
        # should check that url+uri is valid
        self.uri = new_uri

    def add_param(self, key, value):
        # I dont think I will want to check this -- caveat emptor
        self.params[key] = value
        # print(self.params)

    def next_page(self):
        # https://esb.isc-seo.upenn.edu/8091/open_data/course_info/ACCT/?page_number=2&number_of_results_per_page=20
        current = self.params["page_number"]
        self.add_param("page_number", current + 1)

        result_data, service_meta = self.call_api(only_data=False)

        if service_meta["current_page_number"] == current + 1:
            return result_data
        else:
            return None

    def call_api(self, only_data=True):
        url = self.base_url + self.uri
        response = requests.get(url, headers=self.headers, params=self.params)
        response_json = response.json()
        service_meta = response_json["service_meta"]

        if "error_text" in service_meta and service_meta["error_text"]:
            print("error1")
            return "ERROR"
        elif service_meta["current_page_number"] < self.params["page_number"]:
            return response_json["result_data"], service_meta
        elif service_meta["results_per_page"] == len(response_json["result_data"]):
            result_data = response_json["result_data"]
        elif isinstance(response_json["result_data"], list):
            result_data = (
                response_json["result_data"][0]
                if response_json["result_data"]
                else response_json["result_data"]
            )
        else:
            result_data = response_json["result_data"]

        if only_data:
            return result_data
        else:
            return result_data, response_json["service_meta"]

    def get_available_terms(self):
        # this will make a call to
        # https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search_parameters/
        # r['result_data']["available_terms_map"]
        #  "available_terms_map" : {"2013B" : "Summer 2013", "2013C" : "Fall 2013"},
        url = self.base_url + "course_section_search_parameters/"
        response = requests.get(url, headers=self.headers).json()
        # print(response)
        return [*response["result_data"][0]["available_terms_map"]]

    def get_courses_by_term(self, term):
        # https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search?
        # term = 2013C
        self.clear_settings()
        self.set_uri("course_section_search")
        self.add_param("term", term)
        return self.call_api(only_data=True)

    def find_school_by_subj(self, subject):
        """
        returns the two character code
        """
        # https://esb.isc-seo.upenn.edu/8091/open_data/course_info/ACCT/
        # r['result_data'][0]['school_code']
        url = self.base_url + "course_info/" + subject + "/"
        params = {"results_per_page": 2}
        response = requests.get(url, headers=self.headers, params=params).json()
        return response["result_data"][0]["school_code"]

    def get_available_activity(self):
        # this will make a call to
        # https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search_parameters/
        # r['result_data']["activity_map"]
        #  "available_terms_map" : {"2013B" : "Summer 2013", "2013C" : "Fall 2013"},
        url = self.base_url + "course_section_search_parameters/"
        response = requests.get(url, headers=self.headers).json()
        # print(response)
        return response["result_data"][0]["activity_map"]

    def get_available_subj(self):
        url = self.base_url + "course_section_search_parameters/"
        response = requests.get(url, headers=self.headers).json()
        try:
            result = (
                response["service_meta"]["error_text"]
                if response["service_meta"]["error_text"]
                else response["result_data"][0]["departments_map"]
            )
        except Exception as error:
            result = error

        return result


# id_directory = config.get('opendata', 'id_directory')
# key_directory = config.get('opendata', 'key_directory')
# headers_directory = {
#    'Authorization-Bearer' : id,
#    'Authorization-Token':key
# }


# https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search?course_id=ANAT513601

# https://esb.isc-seo.upenn.edu/8091/open_data/directory?last_name=smith&first_name=bob
# def get_instructor(id):
