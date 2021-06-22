import copy
import datetime

import django.core.exceptions
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.utils.html import mark_safe
from markdown import markdown

# This model is to represent a Course object in the CRF
# the meta-data that is important with this is information that will help the course be
# discoverable in the CRF2. all of these objects with be populated from the data
# provided by the Registrar.

# https://docs.djangoproject.com/en/2.1/ref/models/fields/#choices

# add help text: https://docs.djangoproject.com/en/2.1/ref/models/fields/#help-text


"""
profile was created out of a need to store the users penn_id
https://github.com/jlooney/extended-user-example
"""


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    penn_id = models.CharField(max_length=10, unique=True)
    canvas_id = models.CharField(max_length=10, unique=True, null=True)


# class Instructor(models.auth.User):
"""
        this class expands on the User model
"""


class Activity(models.Model):
    name = models.CharField(max_length=40)
    abbr = models.CharField(max_length=3, unique=True, primary_key=True)

    def __str__(self):
        return self.abbr

    def __repr__(self):
        return self.abbr

    def get_name(self):
        return self.abbr

    class Meta:
        verbose_name = "Activity Type"
        verbose_name_plural = "Activity Types"
        ordering = ("abbr",)


#    def __str__(self):
#        return self.username


class School(models.Model):
    """
    mapping of School (i.e. 'Arts & Sciences') to SubjectArea objects
    and their associated subjects
    """

    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True, primary_key=True)
    visible = models.BooleanField(default=True)
    opendata_abbr = models.CharField(max_length=2)
    canvas_subaccount = models.IntegerField(null=True)
    form_additional_enrollments = models.BooleanField(
        default=True, verbose_name="Additional Enrollments Form Field"
    )

    def get_subjects(self):
        return self.subjects

    # def set_subjects(self,visibility):

    def save(self, *args, **kwargs):
        """
        some text
        """
        print("saving school instance")
        # print(self.subjects)
        # print(self.get_subjects())
        print("args,kwargs", args, kwargs)
        subjects = Subject.objects.filter(schools=self.abbreviation)
        print("subjects", subjects)

        for subject in subjects:
            subject.visible = self.visible
            subject.save()
        print("self.pk", self.pk)
        super().save(*args, **kwargs)  # super(Course, self)

    def __str__(self):
        return "%s (%s)" % (self.name, self.abbreviation)

    class Meta:
        ordering = ("name",)
        verbose_name = "School // Sub Account"
        verbose_name_plural = "Schools // Sub Accounts"


class Subject(models.Model):
    """
    mapping of Subject (i.e. 'ANAT' -> Anatomy ) to SubjectArea objects
    requires list_asView but not individual object view
    """

    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True, primary_key=True)
    visible = models.BooleanField(default=True)
    schools = models.ForeignKey(
        School, related_name="subjects", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return "%s (%s)" % (self.name, self.abbreviation)

    class Meta:
        ordering = ("name",)
        verbose_name = "Subject // Deptartment "
        verbose_name_plural = "Subjects // Departments"


class CanvasSite(models.Model):
    """
    this contains all the relevant info about the canvas site once it has been created
    """

    # url = models.URLField()
    canvas_id = models.CharField(
        max_length=10, blank=False, default=None, primary_key=True
    )
    request_instance = models.ForeignKey(
        "Request", on_delete=models.SET_NULL, null=True, default=None, blank=True
    )  # there doesnt have to be one!
    owners = models.ManyToManyField(
        User, related_name="canvas_sites", blank=True
    )  # should be allowed to be null --> "STAFF"
    added_permissions = models.ManyToManyField(
        User, related_name="added_permissions", blank=True, default=None
    )
    name = models.CharField(
        max_length=50, blank=False, default=None
    )  # CHEM 101 2019C General Chemistry I
    sis_course_id = models.CharField(
        max_length=50, blank=True, default=None, null=True
    )  # SRS_CHEM-101-003 2019C
    workflow_state = models.CharField(max_length=15, blank=False, default=None)
    # sis_section_id = models.CharField(max_length=50,blank=False,default=None)#SRS_CHEM-101-003 2019C
    # section_name = models.CharField(max_length=50,blank=False,default=None)#CHEM 101-003 2019C General Chemistry I

    # i think this should be a school object ...
    # subaccount = models.CharField(max_length=50,blank=False,default=None)
    # term = models.CharField(max_length=5,blank=False,default=None)#2019C
    # name = models.CharField(max_length=50,unique=True)#BMIN 521 2019C AI II: Machine Learning
    """
    sis_course_id = #SRS_BMIN-521-401 2019C
    sis_section_id = #SRS_BMIN-521-401 2019C
    section_name = #BMIN 521-401 2019C AI II: Machine Learning
    subaccount = #Perelman School of Medicine
    term = #2019C
    additional_enrollments = models.  #https://stackoverflow.com/questions/1110153/what-is-the-most-efficient-way-to-store-a-list-in-the-django-models
    """

    #
    # def get_additional_enrollements(self):

    def get_owners(self):
        return "\n".join([p.username for p in self.owners.all()])

    def get_added_permissions(self):
        return "\n".join([p.username for p in self.added_permissions.all()])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("canvas_id",)
        verbose_name = "Canvas Site"
        verbose_name_plural = "Canvas Sites"


class CourseManager(models.Manager):
    def has_request(self):
        return super().get_queryset().filter(requested=True)

    # def submitted(self)


class Course(models.Model):

    SPRING = "A"
    SUMMER = "B"
    FALL = "C"

    # dont change these variable names -- used in views.py
    TERM_CHOICES = ((SPRING, "Spring"), (SUMMER, "Summer"), (FALL, "Fall"))

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # id = models.CharField(max_length=250) # this is a number

    owner = models.ForeignKey(
        "auth.User", related_name="created", on_delete=models.CASCADE
    )  # this is who edited it

    instructors = models.ManyToManyField(
        User, related_name="courses", blank=True
    )  # should be allowed to be null --> "STAFF"
    course_term = models.CharField(
        max_length=1,
        choices=TERM_CHOICES,
    )  # self.course_term would == self.SPRING || self.FALL || self.SUMMER
    course_activity = models.ForeignKey(
        Activity, related_name="courses", on_delete=models.CASCADE
    )
    course_code = models.CharField(
        max_length=150, unique=True, primary_key=True, editable=False
    )  # unique and primary_key means that is the lookup_field
    course_subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="courses"
    )  # one to many
    course_primary_subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    course_schools = models.ForeignKey(
        School, related_name="courses", on_delete=models.CASCADE
    )  # one to many
    course_number = models.CharField(max_length=4, blank=False)
    course_section = models.CharField(
        max_length=4, blank=False
    )  # can courses not have associated sections?
    course_name = models.CharField(
        max_length=250
    )  # Human Readable Name i.e. Late Antique Arts
    year = models.CharField(max_length=4, blank=False)
    primary_crosslist = models.CharField(max_length=20, default="", blank=True)
    crosslisted = models.ManyToManyField(
        "self", blank=True, symmetrical=True, default=None
    )
    sections = models.ManyToManyField(
        "self", blank=True, symmetrical=True, default=None
    )
    requested = models.BooleanField(default=False)  # False -> not requested
    # section_request = models.ForeignKey('course.Request',on_delete=models.CASCADE, related_name="additional_sections",default=None,null=True)
    requested_override = models.BooleanField(
        default=False
    )  # this field is just for certain cases !
    multisection_request = models.ForeignKey(
        "course.Request",
        on_delete=models.SET_NULL,
        related_name="additional_sections",
        default=None,
        blank=True,
        null=True,
    )
    crosslisted_request = models.ForeignKey(
        "course.Request",
        on_delete=models.SET_NULL,
        related_name="tied_course",
        default=None,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = (
            "-year",
            "course_code",
        )

    def find_requested(self):
        if self.requested_override == True:
            return True
        else:
            # check if the course has a direct request
            try:
                exists = self.request
                # print("request obj",exists)
                return True
            except:
                # check if the course has been tied into other requests

                exists = self.multisection_request
                exists_cross = self.crosslisted_request
                # print(" multi section request obj",exists)
                if exists or exists_cross:  # check that its not none
                    return True
                else:
                    return False
                return False
        # print("we hit base case that i havent planned for")

    ### wrong logic -- can have diff numbers ###
    def find_crosslisted(self):
        # crosslisted courses hace the same <number><section>_<year><term> -- the difference should be the subject but they should also each have the same primary subject!
        # check that there is a primarycrosslisting
        cross_courses = Course.objects.filter(
            Q(course_primary_subject=self.course_primary_subject)
            & Q(course_number=self.course_number)
            & Q(course_section=self.course_section)
            & Q(course_term=self.course_term)
            & Q(year=self.year)
        )
        # print("found course", cross_courses)
        for course in cross_courses:
            self.crosslisted.add(course)
            self.save()

    ## doesnt work ##
    def update_crosslists(self):
        # makes sure that request override is common
        # makes sure that request object is common ( by setting crosslisted_request)
        cross_courses = Course.objects.filter(
            Q(course_primary_subject=self.course_primary_subject)
            & Q(course_number=self.course_number)
            & Q(course_section=self.course_section)
            & Q(course_term=self.course_term)
            & Q(year=self.year)
        )
        for course in cross_courses:

            course.requested_override = self.requested_override
        try:
            r = self.request
            for course in cross_courses:
                course.crosslisted_request = r
        except:
            pass  # no request

    def save(self, *args, **kwargs):
        """
        some text
        """
        # <subject><course_number><section><year><term>
        self.course_code = (
            self.course_subject.abbreviation
            + self.course_number
            + self.course_section
            + self.year
            + self.course_term
        )
        # print("saving Course instance")
        # print("self.pk",self.pk)
        if self._state.adding == True:  # creating
            # ?#self.requested = self.find_requested()
            # ?#super().save(*args,**kwargs) #super(Course, self)
            # ?#self.sections.set(self.find_sections())
            # ?#self.find_crosslisted()
            super().save(*args, **kwargs)
            # here is where you do the updating of cross listed instances
        else:  # updating

            self.sections.set(self.find_sections())
            self.requested = self.find_requested()
            self.update_crosslists()
            super().save(*args, **kwargs)  # super(Course, self)

    # def set_crosslistings(self):

    def get_request(self):
        try:
            requestinfo = self.request
            print("found request info", requestinfo)
            return requestinfo
        except Request.DoesNotExist:
            print("Request.DoesNotExist!")

        if self.multisection_request:
            return self.multisection_request
        elif self.crosslisted_request:
            return self.crosslisted_request
        else:
            return None

        # return error

    # NOT IN USE AND NEEDS TO BE TESTED
    def get_subjects(self):
        # this need to be
        return self.course_subject.abbreviation
        cross_listed = self.crosslisted
        print(cross_listed)
        if cross_listed == None:
            return self.course_subject.abbreviation
        # should get all crosslisted and the
        return ",\n".join([sub.abbreviation for sub in cross_listed])

    def get_schools(self):
        return self.course_schools
        # return ",\n".join([sch.abbreviation for sch in self.course_schools.all()])

    def get_instructors(self):
        # check if blank?
        # print("lets go to funkie town",self.instructors.all(), )
        if not self.instructors.all().exists():
            return "STAFF"
        return ",\n".join([inst.username for inst in self.instructors.all()])

    def find_sections(self):
        # when all but the course code is the same ?
        # filter all courses that have the same <subj>,<code>, <term>
        # print(
        #     "in get sections",
        #     self.course_subject,
        #     self.course_number,
        #     self.course_term,
        #     self.year,
        # )
        courses = Course.objects.filter(
            Q(course_subject=self.course_subject)
            & Q(course_number=self.course_number)
            & Q(course_term=self.course_term)
            & Q(year=self.year)
        ).exclude(course_code=self.course_code)
        # print("sections", courses)
        return courses

    def srs_format(self):
        term = self.year + self.course_term
        # print(course['course_section'])
        return "%s-%s-%s %s" % (
            self.course_subject.abbreviation,
            self.course_number,
            self.course_section,
            term,
        )

    def srs_format_primary(self, sis_id=True):
        term = self.year + self.course_term
        pc = self.primary_crosslist
        if pc:
            term = pc[-5:]
            section = pc[:-5][-3:]
            number = pc[:-5][:-3][-3:]
            subj = pc[:-5][:-6]
            if sis_id:
                srs_pc = "%s-%s-%s %s" % (subj, number, section, term)
                return srs_pc
            else:
                srs_pc = "%s %s-%s %s" % (subj, number, section, term)
                return srs_pc

        else:
            return self.srs_format()

    def __str__(self):
        return "_".join(
            [
                self.course_subject.abbreviation,
                self.course_number,
                self.course_section,
                self.year + self.course_term,
            ]
        )

    def __unicode__(self):
        return "_".join(
            [
                self.course_subject.abbreviation,
                self.course_number,
                self.course_section,
                self.year,
                self.course_term,
            ]
        )

        # return self.course_code

    objects = models.Manager()
    CourseManager = CourseManager()

    # def get_absolute_url(self):
    #    """
    #    get_absolute_url should return a string of the url that is
    #    associated with that particular model instance. This is
    #    especially useful in templates and redirect responses.
    #    """
    #    # determine which view?
    #    return reverse('vegetable', pks={pk: self.pk})


class Notice(models.Model):
    """
    this is a class that handles system wide notifications
    for earilest and latest methods see: https://simpleisbetterthancomplex.com/tips/2016/10/06/django-tip-17-earliest-and-latest.html
    """

    # TODO
    # [ ] fix __str__ and add better admin table view instead
    # [ ] put on request form not just home page

    creation_date = models.DateTimeField(auto_now_add=True)
    notice_heading = models.CharField(max_length=100)
    notice_text = models.TextField(max_length=1000)  # this should be some html ?
    owner = models.ForeignKey(
        "auth.User", related_name="notices", on_delete=models.CASCADE
    )  # this is who edited it
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "updated_date"  # allows .latest()

    def get_notice_as_markdown(self):
        return mark_safe(markdown(self.notice_text, safe_mode="escape"))

    def __str__(self):

        return (
            "(#"
            + str(self.pk)
            + ") "
            + self.creation_date.strftime("%m-%d-%Y")
            + ': "'
            + self.notice_heading
            + '" by '
            + self.owner.username
        )


# class RequestManager(models.Manager):
#    def submitted(self):


class Request(models.Model):
    REQUEST_PROCESS_CHOICES = (
        ("COMPLETED", "Completed"),
        ("IN_PROCESS", "In Process"),
        ("CANCELED", "Canceled"),
        ("APPROVED", "Approved"),
        ("SUBMITTED", "Submitted"),
        ("LOCKED", "Locked"),
    )
    # The first element in each tuple is the actual value to be set on the model,
    # and the second element is the human-readable name.

    course_requested = models.OneToOneField(
        Course, on_delete=models.CASCADE, primary_key=True
    )  # once the course is deleted the request will be deleted too.

    # additional_sections = models.ForeignKey(Course,null=True,default=None,blank=True,related_name='sections')
    copy_from_course = models.CharField(
        max_length=100, null=True, default=None, blank=True
    )  # previously content source
    # this should be a list of courses they have rights too
    # SuperUsers have access to all courses
    title_override = models.CharField(
        max_length=100, null=True, default=None, blank=True
    )  # previously SRS title override
    additional_instructions = models.TextField(blank=True, default=None, null=True)
    admin_additional_instructions = models.TextField(
        blank=True, default=None, null=True
    )
    reserves = models.BooleanField(default=False)
    # libguide = models.BooleanField(default=False)
    process_notes = models.TextField(blank=True, default="")
    canvas_instance = models.ForeignKey(
        CanvasSite,
        related_name="canvas",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # NOTE! needs something for multisection course sites!

    status = models.CharField(
        max_length=20, choices=REQUEST_PROCESS_CHOICES, default="SUBMITTED"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        "auth.User", related_name="requests", on_delete=models.CASCADE
    )  # should not delete when user is deleted
    masquerade = models.CharField(max_length=20, null=True)
    # additional_enrollments = models.ManyToManyField(AdditionalEnrollment,related_name='additional_enrollments',blank=True)

    class Meta:
        ordering = ["-status", "-created"]  # ('created',)
        # verbose_name = 'Site Request'
        # verbose_name_plural = 'Site Requests'

    def save(self, *args, **kwargs):
        # some text
        # print("saving")
        # print("..",self.status,args,kwargs)
        # print("(Model.py) Request self.pk",self.pk)
        super(Request, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # print("ohhh")
        c = Course.objects.get(course_code=self.course_requested.course_code)

        multisection = Course.objects.filter(multisection_request=c.course_code)
        crosslisted = Course.objects.filter(crosslisted_request=c.course_code)
        if crosslisted:
            for xc in crosslisted:
                xc.crosslisted_request = None
                xc.requested = False
                xc.save()
        if multisection:
            for ms in multisection:
                ms.multisection_request = None
                ms.requested = False
                ms.save()
        print(c.requested)
        super(Request, self).delete()
        c.requested = False
        c.save()
        print(c.requested)

        if crosslisted:
            for xc in crosslisted:
                if c != xc:
                    xc.requested = False
                    xc.save()
        if multisection:
            for ms in multisection:
                ms.requested = False
                ms.save()

    # def __str__(self):
    #    return " \"%s\" site request" % ( self.course_requested.course_code)


class AdditionalEnrollment(models.Model):
    ENROLLMENT_TYPE = (
        ("TA", "TA"),
        ("INST", "Instructor"),
        ("DES", "Designer"),
        ("LIB", "Librarian"),
        ("OBS", "Observer"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=4, choices=ENROLLMENT_TYPE, default="TA")
    course_request = models.ForeignKey(
        Request,
        related_name="additional_enrollments",
        on_delete=models.CASCADE,
        default=None,
    )


# class SubjectArea(models.Model):
"""
 mapping of Subject area code and name. boolean value of displayed in CRF2 or not
 requires list_asView but not individual object view
"""


# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
# see section on Extending User Model Using a One-To-One Link
class AutoAdd(models.Model):
    ROLE_CHOICES = (
        ("TA", "TA"),
        ("INST", "Instructor"),
        ("DES", "Designer"),
        ("LIB", "Librarian"),
        ("OBS", "Observer"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
    )

    # def __str__(self):
    #    return self.

    class Meta:
        ordering = ("user__username",)


class UpdateLog(models.Model):
    """
    this is how to store Task Process history and status
    """

    MANAGER_CHOICES = (
        ("a", "A"),
        ("b", "B"),
        ("c", "C"),
    )

    # consult this: https://medium.freecodecamp.org/how-to-build-a-progress-bar-for-the-web-with-django-and-celery-12a405637440

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    process = models.CharField(max_length=10, choices=MANAGER_CHOICES)
    # log = this should be a link to the log file associated with the task


# This class is to allow any Courseware Support people to edit some of the pages content without halting the appilication


class PageContent(models.Model):

    location = models.CharField(max_length=100)
    markdown_text = models.TextField(max_length=4000)
    updated_date = models.DateTimeField(auto_now=True)

    def get_page_as_markdown(self):
        return mark_safe(markdown(self.markdown_text, safe_mode="escape"))

    def __str__(self):
        return self.location


class RequestSummary(Request):
    class Meta:
        proxy = True
        verbose_name = "Request Summary"
        verbose_name_plural = "Requests Summary"


## this is currently not in use!
class Tools(models.Model):
    """
    this is a table of all tools that we can configure in Canvas
    this should only include tools that can be used in any course at penn
    these are tools that would show up in the side navigation menu
    """

    name = models.CharField(max_length=25, blank=False)

    visibility = models.BooleanField(default=True)

    # schools
