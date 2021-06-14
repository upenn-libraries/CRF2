import collections
import datetime
from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers

from canvas import api
from course.models import *
from course.utils import *

# Serializer Classes provide a way of serializing and deserializing
# the model instances into representations such as json. We can do this
# by declaring serializers that work very similar to Django forms
#


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class CourseSerializer(
    DynamicFieldsModelSerializer
):  # removed HyperlinkedModelSerializer
    """ """

    # # TODO:
    # [ ] make sure that course_SRS_Title is unique ! -- it is used to link later

    # this adds a field that is not defined in the model

    owner = serializers.ReadOnlyField(source="owner.username")
    # cant uncomment following line without resolving lookup for Request
    course_code = serializers.CharField()
    crosslisted = serializers.SlugRelatedField(
        many=True,
        queryset=Course.objects.all(),
        slug_field="course_code",
        required=False,
    )
    # request_info = serializers.HyperlinkedRelatedField(many=False, lookup_field='course_requested',view_name='courses-detail',read_only=True)
    requested = serializers.BooleanField(default=False)
    # multisection_request = serializers.SlugRelatedField(many=False,queryset=Course.objects.all(), slug_field='additional_sections', required=False)
    # requested = serializers.SerializerMethodField(initial=False)
    sections = serializers.SerializerMethodField()  #
    # sections = serializers.SlugRelatedField(many=True,queryset=Course.objects.all(), slug_field='sections')
    # Eventually the queryset should also filter by Group = Instructors
    instructors = serializers.SlugRelatedField(
        many=True, queryset=User.objects.all(), slug_field="username"
    )
    course_schools = serializers.SlugRelatedField(
        many=False, queryset=School.objects.all(), slug_field="abbreviation"
    )
    course_subject = serializers.SlugRelatedField(
        many=False, queryset=Subject.objects.all(), slug_field="abbreviation"
    )
    course_activity = serializers.SlugRelatedField(
        many=False, queryset=Activity.objects.all(), slug_field="abbr"
    )
    id = serializers.ReadOnlyField()
    requested_override = serializers.ReadOnlyField()
    associated_request = serializers.SerializerMethodField()
    # course_requested = serializers.HyperlinkedRelatedField(many=True, view_name='request-detail',read_only=True)
    # request_details = RequestSerializer(many=True,read_only=True)

    class Meta:
        model = Course
        fields = "__all__"  # or a list of field from model like ('','')
        read_only_fields = ("sections",)

    def get_associated_request(self, obj):
        request = obj.get_request()
        if request:
            return request.course_requested.course_code
        else:
            return None

    """
    def get_requested(self, obj):
        # if the object has a request or if it is added as an additional_section in a request

        try:
            exists = obj.request
            print("request obj",exists)
        except:
            return False
        return True
    """

    def get_sections(self, obj):
        # when all but the course code is the same ?
        # filter all courses that have the same <subj>,<code>, <term>
        print("in get sections")
        courses = obj.sections.all()
        result = []
        for course in courses:
            # print(dir(course),course.request)
            result += [
                (course.course_code, course.course_activity.abbr, course.requested)
            ]
        # print("sections",result)
        return result

    def create(self, validated_data):
        """
        Create and return a new 'Course' instance, given the validated_data.
        """
        # print("CourseSerializer validated_data", validated_data)
        instructors_data = validated_data.pop("instructors")
        # schools_data = validated_data.pop('course_schools')
        # subjects_data = validated_data.pop('course_subjects')
        if "crosslisted" in validated_data:
            crosslist = validated_data.pop("crosslisted")
        course = Course.objects.create(**validated_data)
        ##
        ## must loop through adding fields individually because we cannot do direct assignment
        ##
        for instructor_data in instructors_data:
            # print(instructor_data.username, instructor_data)
            course.instructors.add(instructor_data)

        # for school_data in schools_data:
        # print("school_data",school_data)
        #    course.course_schools.add(school_data)

        # for subject_data in subjects_data:
        #    #print("subject data", subject_data)
        #    course.course_subjects.add(subject_data)
        ##print(course.data)
        if "crosslisted" in validated_data:
            ##print(crosslist)
            for cross_course in crosslist:
                ##print("crosslist data", cross_course)
                course.crosslisted.add(cross_course)
        return course

    # this allows the object to be updated!
    def update(self, instance, validated_data):
        """
        Update and return an existing 'Course' instance, given the validated_data.
        """
        # print("validated_data", validated_data)

        # patching - just updating this one thing!
        if len(validated_data) == 1 and "crosslisted" in validated_data.keys():
            instance.crosslisted.set(
                validated_data.get("crosslisted", instance.crosslisted)
            )
            instance.save()
            crosslistings = validated_data.get("crosslisted", instance.crosslisted)

            # this should really not be happening everytime the course is updated??
            for ccourse in crosslistings:
                # print("crosslistings",crosslistings)
                crosslistings.remove(ccourse)
                # make sure to add to exisitng crosslistins and not overwrite them!
                current = ccourse.crosslisted.all()
                # print("current, ccourse, crosslistings",current, ccourse, crosslistings)
                new = list(current) + list(crosslistings)
                # print("new",new)
                ccourse.crosslisted.set(new)
                ccourse.requested = validated_data.get("requested", instance.requested)
            # print("instance serialized",instance)
            return instance
        else:
            instance.course_code = validated_data.get(
                "course_code", instance.course_code
            )
            instance.requested = validated_data.get("requested", instance.requested)
            ##print("whoohooohho",instance.instructors, validated_data.get('instructors',instance.instructors))
            # since theses are nested they need to be treated a little differently
            instance.course_schools.set(
                validated_data.get("course_schools", instance.course_schools)
            )
            instance.instructors.set(
                validated_data.get("instructors", instance.instructors)
            )
            instance.crosslisted.set(
                validated_data.get("crosslisted", instance.crosslisted)
            )

            instance.save()
            crosslistings = validated_data.get("crosslisted", instance.crosslisted)

            # this should really not be happening everytime the course is updated??
            for ccourse in crosslistings:
                # print("crosslistings",crosslistings)
                crosslistings.remove(ccourse)
                # make sure to add to exisitng crosslistins and not overwrite them!
                current = ccourse.crosslisted.all()
                # print("current, ccourse, crosslistings",current, ccourse, crosslistings)
                new = list(current) + list(crosslistings)
                # print("new",new)
                ccourse.crosslisted.set(new)
                ccourse.requested = validated_data.get("requested", instance.requested)
            # print("instance serialized",instance)
            return instance

    # def update_crosslists(crosslisted_courses):


class UserSerializer(serializers.ModelSerializer):
    """ """

    # courses = serializers.HyperlinkedRelatedField(many=True, view_name='course-detail', read_only=True)
    requests = serializers.HyperlinkedRelatedField(
        many=True, view_name="request-detail", read_only=True
    )

    # course_list = CourseSerializer(many=True,read_only=True)
    # this allows to link all the courses with a user
    penn_id = serializers.CharField(source="profile.penn_id")

    class Meta:
        model = User
        fields = (
            "id",
            "penn_id",
            "username",
            "courses",
            "requests",
            "email",
        )  # ,'course_list')
        read_only_fields = ("courses",)
        # because courses is a REVERSE relationship on the User model,
        # it will not be included by default when using the ModelSerializer class
        # so we needed to add an explicit field for it.

    def create(self, validated_data):
        """
        Create and return a new 'User' instance, given the validated data.
        """
        # print(validated_data)
        pennid_data = validated_data.pop("profile")["penn_id"]
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, penn_id=pennid_data)
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing 'User' instance given the validated_data.
        """
        # instance.profile.penn_id = validated_data.get('penn_id', instance.profile.penn_id)
        instance.name = validated_data.get("username", instance.username)

        instance.save()

        return instance


class AdditionalEnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        style={"base_template": "input.html"},
    )
    # role = serializers.SlugRelatedField(many=False, )
    # models.CharField(max_length=4, choices=ENROLLMENT_TYPE,default='TA')
    # course_request = models.ForeignKey(Request,on_delete=models.CASCADE, default=None)

    class Meta:
        model = AdditionalEnrollment
        # fields = '__all__'
        exclude = ("id", "course_request")


class CanvasSiteSerializer(serializers.ModelSerializer):
    # user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username',style={'base_template': 'input.html'})
    # role = serializers.SlugRelatedField(many=False, )
    # models.CharField(max_length=4, choices=ENROLLMENT_TYPE,default='TA')
    # course_request = models.ForeignKey(Request,on_delete=models.CASCADE, default=None)
    owners = serializers.SlugRelatedField(
        many=True, queryset=User.objects.all(), slug_field="username"
    )
    added_permissions = serializers.SlugRelatedField(
        many=True, queryset=User.objects.all(), slug_field="username"
    )

    class Meta:
        model = CanvasSite
        fields = "__all__"

    def validate(self, data):
        # should do more here but oh well
        print("in here")
        return data

    def update(self, instance, validated_data):
        print("vd", validated_data)
        name = validated_data.pop("added_permissions")  # , instance.added_permissions)
        print("name", name)
        for n in name:
            instance.added_permissions.add(n)
        instance.save()
        return instance


class RequestSerializer(DynamicFieldsModelSerializer):  # HyperlinkedModelSerializer
    # this adds a field that is not defined in the model
    # url = serializers.HyperlinkedIdentityField(view_name='UI-requests', looku
    owner = serializers.ReadOnlyField(source="owner.username", required=False)
    course_info = CourseSerializer(source="course_requested", read_only=True)
    canvas_instance = CanvasSiteSerializer(
        read_only=True
    )  # -- doesnt work bc canvassites have p tight permissions?
    masquerade = serializers.ReadOnlyField()
    # additional_sections = CourseSerializer()
    # sections = serializers.SerializerMethodField()

    course_requested = serializers.SlugRelatedField(
        many=False,
        queryset=Course.objects.all(),
        slug_field="course_code",
        style={"base_template": "input.html"},
    )
    title_override = serializers.CharField(
        allow_null=True,
        required=False,
        max_length=45,
        style={"base_template": "input.html"},
    )
    additional_enrollments = AdditionalEnrollmentSerializer(
        many=True,
        default=[],
        style={"base_template": "list_fieldset.html"},
        required=False,
    )
    created = serializers.DateTimeField(format="%I:%M%p %b,%d %Y", required=False)
    updated = serializers.DateTimeField(format="%I:%M%p %b,%d %Y", required=False)
    additional_sections = serializers.SlugRelatedField(
        many=True,
        default=[],
        queryset=Course.objects.all(),
        slug_field="course_code",
        required=False,
    )

    # sections_requested = serializers.SlugRelatedField(many=True,queryset=Course.objects.all(),slug_field='course_code')
    # IF REQUEST STATUS IS CHANGED TO CANCELED IT SHOULD BE DISASSOCIATED FROM COURSE INSTANCE
    # IN ORDER TO PRESERVE THE ONE TO ONE COURSE -> REQUEST RELATIONSHIP
    # IF REQUEST IS MADE THE COURSE INSTANCE SHOULD CHANGE COURSE.REQUESTED to TRUE
    class Meta:
        model = Request
        fields = "__all__"  # or a list of field from model like ('','')
        # exclude = ('masquerade',)
        # depth=2

    def check_for_crf_account(enrollments):
        # [{'user': 'Pennkey', 'role': 'TA'}]
        for enrollment in enrollments:
            print("checking for user, ", enrollment["user"])
            user = validate_pennkey(enrollment["user"])
            if user == None:
                print("we have an error")

    def to_internal_value(self, data):
        data = dict(data)
        if data.get("title_override", None) == "":
            data["title_override"] = None
        if data.get("course_requested", None) == "":
            data["course_requested"] = None
        if data.get("reserves", None) == None:
            data["reserves"] = False
        if data.get("additional_enrollments", None) != None:
            RequestSerializer.check_for_crf_account(data["additional_enrollments"])
        return super(RequestSerializer, self).to_internal_value(data)

    def validate(self, data):
        """
        Check that:
            CourseCopy Course has user or masquerade listed as an instructor
        """
        print("data in validate", data)
        print(data.keys())

        if "additional_enrollments" in data.keys():
            # check if additional_enrollments is not none
            if data["additional_enrollments"] != []:
                for enrollment in data["additional_enrollments"]:
                    print("checking for user, ", enrollment["user"])
                    user = validate_pennkey(enrollment["user"])
                    if user == None:
                        print("error validate pennkey")
                        raise serializers.ValidationError(
                            {
                                "error": (
                                    "an error occurred please check that the pennkey's"
                                    " you entered are correct and add the course"
                                    " information to the additional instructions field."
                                )
                            }
                        )

        # Lets check if we want to update content source and if so, lets check if its valid
        """
        if 'copy_from_course' in data.keys():
            if data['copy_from_course'] == None or data['copy_from_course'] == '':
                print("no copy from course data")
                return data
            #go get course
            print("data['copy_from_course']",data['copy_from_course'])
            instructors = api.get_course_users(data['copy_from_course'])
            user = self.context['request'].user
            masquerade =self.context['request'].session['on_behalf_of']
            print({"instructors":instructors, "user":user, "masquerade":masquerade})
            if user in instructors:
                #validate!
                #print("you taught the course")
                pass
            if masquerade:
                if masquerade in instructors:
                    #validate!
                    #print("you are masqued as some1 who taught the course")
                    pass
            else:
                print("not valid content source")
                #messages.add_message(self.request, messages.ERROR, "an error occurred please add the course information to the additional instructions field and a Courseware Support team memeber will assist you.")
                raise serializers.ValidationError({"error":"an error occurred please add the course information to the additional instructions field and a Courseware Support team memeber will assist you."})
            #if not in the instructors raise an error
            # error message should be like "an error occurred please add the course information to the additional instructions field"
        """
        # if data['owner'] in data['course_info']['instructors']:
        #    raise serializers.ValidationError("you do not have permissions to request this course")
        # print("data was fine")
        return data

    def create(self, validated_data):
        """
        Create and return a new 'Request' instance, given the validated_data.
        Also get associtated Course instance and set course.requested ==True
        """
        # it must also get associated Course instance and set course.requested = True
        # course_requested_data = validated_data.pop('course_requested')
        # check that this course.requested==False
        ##print("course_requested_data", course_requested_data)
        print(
            "validated_Data", validated_data
        )  # {'course_requested': <Course: AAMW_622_401_2019C>, 'additional_enrollments': [], 'copy_from_course': '', 'status': 'SUBMITTED', 'masquerade': '', 'owner': <SimpleLazyObject: <User: mfhodges>>}

        add_enrolls_data = validated_data.pop("additional_enrollments")
        add_sections_data = validated_data.pop("additional_sections")
        # CHECK FOR AUTOADDS AND THEN ADD !
        # check for school and then check for subject
        autoadds = AutoAdd.objects.filter(
            school=validated_data["course_requested"].course_schools
        ).filter(subject=validated_data["course_requested"].course_subject)

        request_object = Request.objects.create(**validated_data)
        # validated_data['course_requested'].requested = False
        if add_enrolls_data:
            print("add_enrolls_data", add_enrolls_data)
            for enroll_data in add_enrolls_data:
                ##print("subject data", subject_data)
                print("enroll_data", enroll_data)
                AdditionalEnrollment.objects.create(
                    course_request=request_object, **enroll_data
                )
                # request_object.additional_enrollments.add(enroll_data)
        if autoadds:
            for autoadd in autoadds:
                print(autoadd)
                # [OrderedDict([('user', <User: mollyk>), ('role', 'DES')])]

                enroll_data = collections.OrderedDict(
                    [("user", autoadd.user), ("role", autoadd.role)]
                )
                AdditionalEnrollment.objects.create(
                    course_request=request_object, **enroll_data
                )

        if add_sections_data:
            print("add_sections_data", add_sections_data)
            for section_data in add_sections_data:
                # we need to add point the multisection_request to this request
                print("section_data", section_data)
                section = Course.objects.get(course_code=section_data.course_code)
                section.multisection_request = request_object
                section.save()

                # FINISH
        course = validated_data["course_requested"]
        if course.crosslisted.all():
            print("instance.crosslisted", course.crosslisted.all())
            for xc in course.crosslisted.all():
                if course != xc:
                    xc.crosslisted_request = request_object
                    xc.save()
        # print("RequestSerializer.create", validated_data)
        return request_object

    # this allows the object to be updated!
    def update(self, instance, validated_data):
        """
        Update and return an existing 'Request' instance, given the validated_data.
        If the status field is present no other information should be updated this is to resolve the issue of clearing all form information when you approve a request
        """

        print("in serializer update ", validated_data)
        new_status = validated_data.get("status", None)
        print("new_status, instance.status", new_status, instance.status)

        if new_status:
            print("status change all other changes are ignored")
            instance.status = new_status
            instance.save()
            return instance
        instance.status = validated_data.get("status", instance.status)
        instance.title_override = validated_data.get(
            "title_override", instance.title_override
        )
        instance.copy_from_course = validated_data.get(
            "copy_from_course", instance.copy_from_course
        )
        instance.reserves = validated_data.get("reserves", instance.reserves)
        instance.additional_instructions = validated_data.get(
            "additional_instructions", instance.additional_instructions
        )
        instance.admin_additional_instructions = validated_data.get(
            "admin_additional_instructions", instance.admin_additional_instructions
        )

        if instance.reserves == None:
            print("instance.reserves", instance.reserves)

        add_enrolls_data = validated_data.get("additional_enrollments")
        if add_enrolls_data:
            # request_obj =
            AdditionalEnrollment.objects.filter(course_request=instance).delete()
            for enroll_data in add_enrolls_data:
                ##print("subject data", subject_data)
                # print("instance",instance)
                print("enroll_data", enroll_data)
                AdditionalEnrollment.objects.update_or_create(
                    course_request=instance, **enroll_data
                )
                # request_object.additional_enrollments.add(enroll_data)

        add_sections_data = validated_data.get("additional_sections")
        c_data = instance.additional_sections.all()  # .update()
        print("c_data", c_data)
        c_copy = deepcopy(c_data)

        print(instance.status, "STATUS")
        if add_sections_data or instance.additional_sections.all():
            print("instance.", instance)
            # now that the relationship has been removed - there is still some other params to fix
            print("c_data2", c_data)
            for course in c_data:
                course.multisection_request = None
                course.requested = False
                course.save()
                print("course.requested", course.requested)
            print("instance..", instance)
            instance.additional_sections.clear()
            # instance.additional_sections.set()
            print("2instance.additional_sections", instance.additional_sections.all())
            print("add_sections_data", add_sections_data)
            for section_data in add_sections_data:
                # we need to add point the multisection_request to this request
                print("section_data", section_data.course_code)
                section = Course.objects.get(course_code=section_data.course_code)
                section.multisection_request = instance
                section.save()
                print("section.requested", section.requested)

        # instance.additional_enrollments = validated_data.set('additional_enrollments',instance.additional_enrollments)
        # print("instance.status", instance.status)
        # print("instance.title_override", instance.title_override)
        # instance.course = validated_data.get('course_requested', instance.course_requested)
        instance.save()

        print("c_Data", c_data)
        print("c_copy", c_copy)
        print("3instance.additional_sections", instance.additional_sections.all())
        # print('additional_instructions',validated_data.get('additional_instructions',instance.additional_instructions))
        # print('reserves',validated_data.get('reserves',instance.reserves))
        return instance


class SubjectSerializer(serializers.ModelSerializer):
    """ """

    # id = serializers.ReadOnlyField()# allows in templates to call subject.id to get pk

    class Meta:
        model = Subject
        fields = "__all__"

    def create(self, validated_data):
        """
        Create and return a new 'Subject' instance, given the validated data.
        """
        # print("subject validated_data", validated_data)
        # something for school?
        # schools_data = validated_data.pop('schools')
        ##print(schools_data)
        ##print("validated_data", validated_data)
        return Subject.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'Subject' instance given the validated_data.
        """
        # print("ATTEMPTING TO UPDATE SUBJECT")
        # print("conext['format']",self.context['format'])

        instance.name = validated_data.get("name", instance.name)
        instance.abbreviation = validated_data.get(
            "abbreviation", instance.abbreviation
        )
        instance.visible = validated_data.get("visible", instance.visible)
        # instance.subject = validated_data.get('school',instance.school)
        # something for school?
        instance.save()

        return instance


class SchoolSerializer(serializers.ModelSerializer):
    """ """

    # id = serializers.ReadOnlyField() # allows in templates to call school.id to get pk
    # associated =  serializers.SlugRelatedField(many=False,queryset=Subject.objects.all(), slug_field='abbreviation', style={'base_template': 'input.html'})
    # subjects = serializers.SlugRelatedField(many=False,queryset=Subject.objects.all(), slug_field='abbreviation', style={'base_template': 'input.html'})

    subjects = SubjectSerializer(many=True, read_only=True)
    # subjects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)#serializers.StringRelatedField(many=True)#SubjectSerializer(many=True, source='schools_associated')

    class Meta:
        model = School
        fields = (
            "name",
            "abbreviation",
            "visible",
            "subjects",
            "canvas_subaccount",
        )  #'__all__'

    def create(self, validated_data):
        """
        Create and return a new 'School' instance, given the validated data.
        """
        # print("validated_data", validated_data)
        # subjects = validated_data.pop('subjects')
        ##print("subjects",subjects)

        # something for subjects?

        return School.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'School' instance given the validated_data.
        """
        # print("(serializer.py ATTEMPTING TO UPDATE SCHOOL")
        # print("conext['format']",self.context['format'])

        instance.name = validated_data.get("name", instance.name)
        instance.abbreviation = validated_data.get(
            "abbreviation", instance.abbreviation
        )
        instance.visible = validated_data.get("visible", instance.visible)
        instance.canvas_subaccount = validated_data.get(
            "canvas_subaccount", instance.canvas_subaccount
        )
        # instance.subject = validated_data.get('')
        # something for subjects
        instance.save()

        return instance


class NoticeSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    id = serializers.ReadOnlyField()

    class Meta:
        model = Notice
        fields = "__all__"

    def create(self, validated_data):
        """
        Create and return a new 'Notice' instance, given the validated data.
        """
        return Notice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'Notice' instance given the validated_data.
        """
        instance.notice_text = validated_data.get("notice_text", instance.notice_text)
        instance.save()
        return instance


class AutoAddSerializer(serializers.HyperlinkedModelSerializer):
    # Eventually the queryset should also filter by Group = Instructors
    # for more info on base_template style see: https://www.django-rest-framework.org/topics/html-and-forms/#field-styles ( table at the end of page)
    user = serializers.SlugRelatedField(
        many=False,
        queryset=User.objects.all(),
        slug_field="username",
        style={"base_template": "input.html"},
    )
    school = serializers.SlugRelatedField(
        many=False, queryset=School.objects.all(), slug_field="abbreviation"
    )
    subject = serializers.SlugRelatedField(
        many=False,
        queryset=Subject.objects.all(),
        slug_field="abbreviation",
        style={"base_template": "input.html"},
    )
    id = serializers.ReadOnlyField()

    class Meta:
        model = AutoAdd
        fields = "__all__"

    """
    def to_internal_value(self, data):
        #('TA','TA'),
        #('INST','Instructor'),
        #('DES','Designer'),
        #('LIB','Librarian'),
        #('OBS', 'Observer'),)
        data = dict(data)
        print("AHHHHH",data)
        if data.get('role', None) == 'librarian':

            data['role'] ='LIB'

        return super(AutoAddSerializer, self).to_internal_value(data)
    """

    def create(self, validated_data):
        """
        Create and return a new 'Notice' instance, given the validated data.
        """
        return AutoAdd.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'Notice' instance given the validated_data.
        """
        # instance.notice_text = validated_data.get('notice_text', instance.notice_text)
        instance.save()
        return instance


class UpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateLog
        fields = "__all__"

    def create(self, validated_data):
        """
        Create and return a new 'UpdateLog' instance, given the validated data.
        """
        return AutoAdd.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'UpdateLog' instance given the validated_data.
        """
        # instance.notice_text = validated_data.get('notice_text', instance.notice_text)
        instance.save()
        return instance
