from rest_framework import serializers
from course.models import Course, Notice, Request, School, Subject, AutoAdd, UpdateLog,Profile
from django.contrib.auth.models import User
import datetime
from django.contrib import messages
from canvas import api
# Serializer Classes provide a way of serializing and deserializing
# the model instances into representations such as json. We can do this
# by declaring serializers that work very similar to Django forms
#








class CourseSerializer(serializers.ModelSerializer): #removed HyperlinkedModelSerializer
    """

    """

    # # TODO:
    # [ ] make sure that course_SRS_Title is unique ! -- it is used to link later

    #this adds a field that is not defined in the model

    owner = serializers.ReadOnlyField(source='owner.username')
    # cant uncomment following line without resolving lookup for Request
    course_code = serializers.CharField()
    crosslisted = serializers.SlugRelatedField(many=True,queryset=Course.objects.all(), slug_field='course_code', required=False)
    #request_info = serializers.HyperlinkedRelatedField(many=False, lookup_field='course_requested',view_name='courses-detail',read_only=True)

    #request_status = serializers.HyperlinkedIdentityField(view_name='course-request', format='html')


    # Eventually the queryset should also filter by Group = Instructors
    instructors = serializers.SlugRelatedField(many=True,queryset=User.objects.all(), slug_field='username')
    course_schools = serializers.SlugRelatedField(many=True,queryset=School.objects.all(), slug_field='abbreviation')
    course_subject = serializers.SlugRelatedField(many=False,queryset=Subject.objects.all(), slug_field='abbreviation')

    id = serializers.ReadOnlyField()
    #course_requested = serializers.HyperlinkedRelatedField(many=True, view_name='request-detail',read_only=True)
    #request_details = RequestSerializer(many=True,read_only=True)

    class Meta:
        model = Course
        fields = '__all__' # or a list of field from model like ('','')
        #read_only_fields = ('requested',)




    def create(self, validated_data):
        """
        Create and return a new 'Course' instance, given the validated_data.
        """
        #print("CourseSerializer validated_data", validated_data)
        instructors_data = validated_data.pop('instructors')
        schools_data = validated_data.pop('course_schools')
        #subjects_data = validated_data.pop('course_subjects')
        if 'crosslisted' in validated_data: crosslist = validated_data.pop('crosslisted')
        course = Course.objects.create(**validated_data)
        ##
        ## must loop through adding fields individually because we cannot do direct assignment
        ##
        for instructor_data in instructors_data:
            #print(instructor_data.username, instructor_data)
            course.instructors.add(instructor_data)

        for school_data in schools_data:
            #print("school_data",school_data)
            course.course_schools.add(school_data)

        #for subject_data in subjects_data:
        #    #print("subject data", subject_data)
        #    course.course_subjects.add(subject_data)
        ##print(course.data)
        if 'crosslisted' in validated_data:
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
        #print("validated_data", validated_data)

        # patching - just updating this one thing!
        if len(validated_data) ==1 and 'crosslisted' in validated_data.keys():
            instance.crosslisted.set(validated_data.get('crosslisted',instance.crosslisted))
            instance.save()
            crosslistings = validated_data.get('crosslisted',instance.crosslisted)

            # this should really not be happening everytime the course is updated??
            for ccourse in crosslistings:
                #print("crosslistings",crosslistings)
                crosslistings.remove(ccourse)
                # make sure to add to exisitng crosslistins and not overwrite them!
                current = ccourse.crosslisted.all()
                #print("current, ccourse, crosslistings",current, ccourse, crosslistings)
                new = list(current) + list(crosslistings)
                #print("new",new)
                ccourse.crosslisted.set(new)
                ccourse.requested = validated_data.get('requested',instance.requested)
            #print("instance serialized",instance)
            return instance
        else:
            instance.course_code = validated_data.get('course_code', instance.course_code)
            instance.requested = validated_data.get('requested',instance.requested)
            ##print("whoohooohho",instance.instructors, validated_data.get('instructors',instance.instructors))
            # since theses are nested they need to be treated a little differently
            instance.course_schools.set(validated_data.get('course_schools', instance.course_schools))
            instance.instructors.set(validated_data.get('instructors',instance.instructors))
            instance.crosslisted.set(validated_data.get('crosslisted',instance.crosslisted))
            instance.save()
            crosslistings = validated_data.get('crosslisted',instance.crosslisted)

            # this should really not be happening everytime the course is updated??
            for ccourse in crosslistings:
                #print("crosslistings",crosslistings)
                crosslistings.remove(ccourse)
                # make sure to add to exisitng crosslistins and not overwrite them!
                current = ccourse.crosslisted.all()
                #print("current, ccourse, crosslistings",current, ccourse, crosslistings)
                new = list(current) + list(crosslistings)
                #print("new",new)
                ccourse.crosslisted.set(new)
                ccourse.requested = validated_data.get('requested',instance.requested)
            #print("instance serialized",instance)
            return instance

    #def update_crosslists(crosslisted_courses):



"""
CROSS LISTING UPDATE ISSUE
Currently bc of the ManyToMany self relationship of cross listing if we have course A and update it
so it is cross listed with B, C and D the resulting courses crosslistings would be:

    A       B       C          D
   ---     ---     ---        ---
    B       A       A          A
    C
    D

But we want
    A       B       C          D
   ---     ---     ---        ---
    B       A       A          A
    C       C       B          B
    D       D       D          C



"""
class UserSerializer(serializers.ModelSerializer):
    """

    """

    #courses = serializers.HyperlinkedRelatedField(many=True, view_name='course-detail', read_only=True)
    requests = serializers.HyperlinkedRelatedField(many=True, view_name='request-detail',read_only=True)

    #course_list = CourseSerializer(many=True,read_only=True)
    # this allows to link all the courses with a user
    penn_id = serializers.CharField(source='profile.penn_id')

    class Meta:
        model = User
        fields = ('id', 'penn_id','username', 'courses','requests', 'email')#,'course_list')
        read_only_fields = ('courses',)
        # because courses is a REVERSE relationship on the User model,
        # it will not be included by default when using the ModelSerializer class
        # so we needed to add an explicit field for it.

    def create(self,validated_data):
        """
        Create and return a new 'User' instance, given the validated data.
        """
        #print(validated_data)
        pennid_data = validated_data.pop('profile')['penn_id']
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user,penn_id=pennid_data)
        return user


    def update(self, instance, validated_data):
        """
        Update and return an existing 'User' instance given the validated_data.
        """
        #instance.profile.penn_id = validated_data.get('penn_id', instance.profile.penn_id)
        instance.name = validated_data.get('username', instance.username)

        instance.save()

        return instance



class RequestSerializer(serializers.ModelSerializer): #HyperlinkedModelSerializer
    #this adds a field that is not defined in the model
    #url = serializers.HyperlinkedIdentityField(view_name='UI-requests', looku
    owner = serializers.ReadOnlyField(source='owner.username')
    course_info = CourseSerializer(source='course_requested', read_only=True)
    masquerade = serializers.ReadOnlyField()

    course_requested = serializers.SlugRelatedField(many=False,queryset=Course.objects.all(), slug_field='course_code' , style={'base_template': 'input.html'})
    title_override = serializers.CharField(required=False , style={'base_template': 'input.html'})

    # IF REQUEST STATUS IS CHANGED TO CANCELED IT SHOULD BE DISASSOCIATED FROM COURSE INSTANCE
    # IN ORDER TO PRESERVE THE ONE TO ONE COURSE -> REQUEST RELATIONSHIP
    # IF REQUEST IS MADE THE COURSE INSTANCE SHOULD CHANGE COURSE.REQUESTED to TRUE
    class Meta:
        model = Request
        fields = '__all__' # or a list of field from model like ('','')
        #exclude = ('masquerade',)
        #depth=2

    def validate(self, data):
        """
        Check that:
            CourseCopy Course has user or masquerade listed as an instructor
        """
        if data['copy_from_course']:
            #go get course
            #print("data['copy_from_course']",data['copy_from_course'])
            instructors = api.get_course_users(data['copy_from_course'])
            user = self.context['request'].user
            masquerade =self.context['request'].session['on_behalf_of']
            ##print(instructors)
            ##print(user)
            ##print(masquerade)
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
                #print("found error")
                #messages.add_message(request, messages.ERROR, 'errror text')
                raise serializers.ValidationError(_("an error occurred please add the course information to the additional instructions field"))
            #if not in the instructors raise an error
            # error message should be like "an error occurred please add the course information to the additional instructions field"


        ##print(data)
        ##print(self.instance)
        ##print('data[owner]',data['owner'])
        ##print('data[masquerade]', data['masquerade'])
        ##print("data['course_info']", data['course_info'])
        #if data['owner'] in data['course_info']['instructors']:
        #    raise serializers.ValidationError("you do not have permissions to request this course")
        #print("data was fine")
        return data


    def create(self, validated_data):
        """
        Create and return a new 'Request' instance, given the validated_data.
        Also get associtated Course instance and set course.requested ==True
        """
        # it must also get associated Course instance and set course.requested = True
        #course_requested_data = validated_data.pop('course_requested')
        # check that this course.requested==False
        ##print("course_requested_data", course_requested_data)
        #print("validated_Data",validated_data)

        add_enrolls_data = validated_data.pop('additional_enrollments')
        request_object = Request.objects.create(**validated_data)
        #validated_data['course_requested'].requested = False

        for enroll_data in add_enrolls_data:
            ##print("subject data", subject_data)
            request_object.additional_enrollments.add(enroll_data)

        #print("RequestSerializer.create", validated_data)
        return request_object

    # this allows the object to be updated!
    def update(self, instance, validated_data):
        """
        Update and return an existing 'Request' instance, given the validated_data.
        """
        # TODO
        # [ ]must check that the course is not already requested?
        # [ ] better/more thorough validation

        #print("in serializer ", validated_data)
        instance.status = validated_data.get('status',instance.status)
        instance.title_override = validated_data.get('title_override',instance.title_override)
        instance.copy_from_course = validated_data.get('copy_from_course',instance.copy_from_course)
        instance.reserves = validated_data.get('reserves',instance.reserves)
        instance.additional_instructions = validated_data.get('additional_instructions',instance.additional_instructions)
        #print("instance.status", instance.status)
        #print("instance.title_override", instance.title_override)
        #instance.course = validated_data.get('course_requested', instance.course_requested)
        instance.save()
        #print('additional_instructions',validated_data.get('additional_instructions',instance.additional_instructions))
        #print('reserves',validated_data.get('reserves',instance.reserves))
        return instance

class SubjectSerializer(serializers.ModelSerializer):
    """

    """
    #id = serializers.ReadOnlyField()# allows in templates to call subject.id to get pk

    class Meta:
        model = Subject
        fields = '__all__'

    def create(self,validated_data):
        """
        Create and return a new 'Subject' instance, given the validated data.
        """
        #print("subject validated_data", validated_data)
        #something for school?
        #schools_data = validated_data.pop('schools')
        ##print(schools_data)
        ##print("validated_data", validated_data)
        return Subject.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing 'Subject' instance given the validated_data.
        """
        #print("ATTEMPTING TO UPDATE SUBJECT")
        #print("conext['format']",self.context['format'])

        instance.name = validated_data.get('name', instance.name)
        instance.abbreviation = validated_data.get('abbreviation', instance.abbreviation)
        instance.visible = validated_data.get('visible', instance.visible)
        #instance.subject = validated_data.get('school',instance.school)
        #something for school?
        instance.save()

        return instance



class SchoolSerializer(serializers.ModelSerializer):
    """

    """
    #id = serializers.ReadOnlyField() # allows in templates to call school.id to get pk
    #associated =  serializers.SlugRelatedField(many=False,queryset=Subject.objects.all(), slug_field='abbreviation', style={'base_template': 'input.html'})
    #subjects = serializers.SlugRelatedField(many=False,queryset=Subject.objects.all(), slug_field='abbreviation', style={'base_template': 'input.html'})

    subjects = SubjectSerializer(many=True,read_only=True)
    #subjects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)#serializers.StringRelatedField(many=True)#SubjectSerializer(many=True, source='schools_associated')

    class Meta:
        model = School
        fields = ('name','abbreviation','visible','subjects','canvas_subaccount')#'__all__'

    def create(self,validated_data):
        """
        Create and return a new 'School' instance, given the validated data.
        """
        #print("validated_data", validated_data)
        #subjects = validated_data.pop('subjects')
        ##print("subjects",subjects)

        #something for subjects?


        return School.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing 'School' instance given the validated_data.
        """
        #print("(serializer.py ATTEMPTING TO UPDATE SCHOOL")
        #print("conext['format']",self.context['format'])

        instance.name = validated_data.get('name', instance.name)
        instance.abbreviation = validated_data.get('abbreviation', instance.abbreviation)
        instance.visible = validated_data.get('visible', instance.visible)
        instance.canvas_subaccount = validated_data.get('canvas_subaccount', instance.canvas_subaccount)
        #instance.subject = validated_data.get('')
        #something for subjects
        instance.save()

        return instance




class NoticeSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    id = serializers.ReadOnlyField()

    class Meta:
        model = Notice
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new 'Notice' instance, given the validated data.
        """
        return Notice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'Notice' instance given the validated_data.
        """
        instance.notice_text = validated_data.get('notice_text', instance.notice_text)
        instance.save()
        return instance




class AutoAddSerializer(serializers.HyperlinkedModelSerializer):
    # Eventually the queryset should also filter by Group = Instructors
    # for more info on base_template style see: https://www.django-rest-framework.org/topics/html-and-forms/#field-styles ( table at the end of page)
    user = serializers.SlugRelatedField(many=False,queryset=User.objects.all(), slug_field='username',  style={'base_template': 'input.html'})
    school = serializers.SlugRelatedField(many=False,queryset=School.objects.all(), slug_field='abbreviation')
    subject = serializers.SlugRelatedField(many=False,queryset=Subject.objects.all(), slug_field='abbreviation', style={'base_template': 'input.html'})
    id = serializers.ReadOnlyField()
    class Meta:
        model = AutoAdd
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new 'Notice' instance, given the validated data.
        """
        return AutoAdd.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'Notice' instance given the validated_data.
        """
        #instance.notice_text = validated_data.get('notice_text', instance.notice_text)
        instance.save()
        return instance


class UpdateLogSerializer(serializers.ModelSerializer):


    class Meta:
        model = UpdateLog
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new 'UpdateLog' instance, given the validated data.
        """
        return AutoAdd.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'UpdateLog' instance given the validated_data.
        """
        #instance.notice_text = validated_data.get('notice_text', instance.notice_text)
        instance.save()
        return instance
