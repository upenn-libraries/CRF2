from course.models import *
from django.core.management.base import BaseCommand
import sys
import os
import csv


class Command(BaseCommand):
    help = 'Output csv containing comprehensive list of each course in the CRF and whether it has been requested.'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--term', type=str, help='Define a term ( e.g. 2019A )')

    def handle(self, *args, **kwargs):
        outputfile = 'CourseRequestSummary.csv'
        my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        output_path = os.path.join(my_path, 'ACP/data', outputfile)
        fieldnames = ('Section', 'Title', 'Activity', 'Instructor', 'Requested?')
        year = kwargs['term'][:-1]
        course_term = kwargs['term'][-1].upper()
        courses = Course.objects.filter(year=year, course_term=course_term)
        sys.stdout.write("Preparing to write %d records to %s\n" % (courses.count(), output_path))
        with open(output_path, 'w') as c:
            w = csv.DictWriter(c, fieldnames=fieldnames)
            w.writeheader()
            for c in courses:
                instructor = 'STAFF'
                if c.instructors.count() == 1:
                    instructor = c.instructors.first().last_name
                elif c.instructors.count() > 1:
                    instructor = ', '.join([x[0] for x in c.instructors.values_list('last_name')])
                w.writerow(dict(
                    zip(fieldnames, (c.course_code, c.course_name, c.course_activity.abbr, instructor, c.requested))))
