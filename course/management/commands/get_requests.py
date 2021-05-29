from course.models import *
from django.core.management.base import BaseCommand
from crf2.settings import BASE_DIR
from django.utils.crypto import get_random_string
from course.utils import *
from configparser import ConfigParser
import json
from OpenData.library import *
from canvasapi import Canvas
import logging
import sys
import os
import csv
import os
import sys

from django.core.management.base import BaseCommand

from course.models import *

config = ConfigParser()
config.read("config/config.ini")


class Command(BaseCommand):
    help = "output requests"

    """
    FROM MODELS
        course_term = models.CharField(
            max_length=1,choices = TERM_CHOICES,) # self.course_term would == self.SPRING || self.FALL || self.SUMMER
        course_activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
        course_code = models.CharField(max_length=150,unique=True, primary_key=True, editable=False) # unique and primary_key means that is the lookup_field
        course_subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='courses') # one to many
        course_primary_subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
        course_schools = models.ManyToManyField(School,related_name='courses')# one to many
        course_number = models.CharField(max_length=4, blank=False)
        course_section = models.CharField(max_length=4,blank=False)# can courses not have associated sections?
        course_name = models.CharField(max_length=250) # Human Readable Name i.e. Late Antique Arts
        year = models.CharField(max_length=4,blank=False)
        crosslisted = models.ManyToManyField("self", blank=True, symmetrical=True, default=None)
        requested =  models.BooleanField(default=False)# False -> not requested
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-t", "--term", type=str, help="Define a term ( e.g. 2019A )"
        )
        parser.add_argument(
            "-d", "--opendata", action="store_true", help="pull from OpenData API"
        )
        parser.add_argument(
            "-l", "--localstore", action="store_true", help="pull from Local Store"
        )  # not

        # parser.add_argument('-p', '--prefix', type=str, help='Define a username prefix')
        # parser.add_argument('-a', '--admin', action='store_true', help='Create an admin account')
        # parser.add_argument('-c', '--courseware', action='store_true', help='Quick add Courseware Support team as Admins')

        # Need to check to see if updates need to be done
        #

    def handle(self, *args, **kwargs):
        outputfile = "RequestSummary.csv"
        my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        API_URL = config.get("canvas", "prod_env")  #'prod_env')
        API_KEY = config.get("canvas", "prod_key")  #'prod_key')
        canvas = Canvas(API_URL, API_KEY)
        outFile = open(os.path.join(my_path, "ACP/data", outputfile), "w+")
        requests = Request.objects.all()
        outFile.write("course_code, subaccount, status, provisioned, date_created\n")
        total = requests.count()
        counter = 1
        for r in requests:
            if counter % 25 == 0:
                print("%s/%s done" % (counter, total))
            course_code = r.course_requested.course_code
            try:
                subaccount = r.course_requested.course_schools.abbreviation
            except:
                subaccount = "NA"
            try:
                status = r.canvas_instance.workflow_state
            except:
                status = "NA"

            try:
                canvas_course = canvas.get_course(r.canvas_instance.canvas_id)
                datecreated = canvas_course.created_at
            except:
                datecreated = "NA"

            provisioned = ""
            outFile.write(
                "%s,%s,%s,%s,%s\n"
                % (course_code, subaccount, status, provisioned, datecreated)
            )
            counter += 1
