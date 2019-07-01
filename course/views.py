
from course.models import * #Course, Notice, Request, School, Subject, AutoAdd
from course.serializers import * #CourseSerializer, UserSerializer, NoticeSerializer, RequestSerializer, SchoolSerializer, SubjectSerializer, AutoAddSerializer
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from course.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.reverse import reverse
from django.utils.datastructures import MultiValueDict
from rest_framework.utils import html
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.http.request import QueryDict
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.views.generic import TemplateView
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import path
from course import views

from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.utils.urls import replace_query_param, remove_query_param
from django_filters import rest_framework as filters
from django.contrib.auth.mixins import LoginRequiredMixin

from course.forms import ContactForm, EmailChangeForm
from django.template.loader import get_template
import datetime
from course import email_processor
from course import utils
import json
from rest_framework.exceptions import PermissionDenied
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
#from rest_framework.filters import SearchFilter
#class CourseView(TemplateView):
#    template_name = "index.html"


"""
For more 'Detailed descriptions, with full methods and attributes, for each
of Django REST Framework's class-based views and serializers'see: http://www.cdrf.co/

"""

#self.request.QUERY_PARAMS.get('appKey', None)


######### API METHODS ########
# PUT/PATCH -> PARTIAL UPDATE
# POST -> CREATE

# for more on viewsets see: https://www.django-rest-framework.org/api-guide/viewsets/
# (slightly helpful ) or see: http://polyglot.ninja/django-rest-framework-viewset-modelviewset-router/

#######################################
########## ERROR VIEWS ###############
######################################

from rest_framework.views import exception_handler
from rest_framework import status



def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    ##print("helloooo","\n",exc,"\n",context)
    response = exception_handler(exc, context)
    #response = render({},'errors/403.html')


    # we need to be able to parse if they are doing a html request or not
    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['error'] = response.data['detail']
        del response.data['detail']

    #response.template_name = 'base_blank.html'#'errors/'+str(response.status_code)+'.html'
    #print("we r barely ali", response.data['status_code'])
    return response
    #return render(response, 'errors/'+str(response.status_code) +'.html')



class MixedPermissionModelViewSet(viewsets.ModelViewSet): #LoginRequiredMixin, -- causes problems with API?
    '''
    Mixed permission base model allowing for action level
    permission control. Subclasses may define their permissions
    by creating a 'permission_classes_by_action' variable.

    Example:
    permission_classes_by_action = {'list': [AllowAny],
                                   'create': [IsAdminUser]}

    Since each viewset extends the modelviewset there are default actions that are included...
        for each action there should be a defined permission.
    see more here: http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html

    THIS MODEL IS INHERITED BY EVERY VIEWSET ( except homepage... ) !!
    '''
    permission_classes_by_action = {}
    login_url = '/accounts/login/'
    #permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        #print("we here")

        try:
            print("self.action", self.action)
            # return permission_classes depending on `action`
            #print([permission() for permission in self.permission_classes_by_action[self.action]])
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            print("KeyError for permission: ", self.action)
            return [permission() for permission in self.permission_classes]


    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())





class CourseFilter(filters.FilterSet):
    #activity =
    #filter_fields = ('course_activity','instructors__username','course_schools__abbreviation','course_subjects__abbreviation',) #automatically create a FilterSet class
    # https://github.com/philipn/django-rest-framework-filters/issues/102
    #pls see: https://django-filter.readthedocs.io/en/master/ref/filters.html
    #https://django-filter.readthedocs.io/en/master/ref/filters.html#modelchoicefilter
    activity = filters.ModelChoiceFilter(queryset=Activity.objects.all(), field_name='course_activity', label='Activity')
    instructor = filters.CharFilter(field_name='instructors__username', label='Instructor')
    school = filters.CharFilter(field_name='course_schools__abbreviation',label='School (abbreviation)')
    subject = filters.CharFilter(field_name='course_subject__abbreviation', label='Subject (abbreviation)')
    term = filters.ChoiceFilter(choices=Course.TERM_CHOICES, field_name='course_term', label='Term')
    class Meta:
        model = Course
        fields = ['instructor','subject','term','activity','school']#,'activity', school


class CourseViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions. see http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html
    """
    # # TODO:
    # [ ] create and test permissions
    # [x] on creation of request instance mutatate course instance so courese.requested = True
    #[x ] ensure POST is only setting masquerade
    lookup_field = 'course_code'


    queryset = Course.objects.filter(~Q(course_subject__visible=False)).exclude(course_schools__visible=False,) #this should be filtered by the
    serializer_class = CourseSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,)
    #filter_backends = ( SearchFilter)
    search_fields = ('$course_name','$course_code',)
    filterset_class = CourseFilter


    # for permission_classes_by_action see: https://stackoverflow.com/questions/35970970/django-rest-framework-permission-classes-of-viewset-method
    permission_classes_by_action = {'create': [IsAdminUser],
                                    'list': [IsAuthenticated],
                                    'retrieve':[IsAuthenticated],#,IsAdminUser], # it seems like it defaults to the most strict case
                                    'update':[IsAdminUser],
                                    'partial_update':[IsAdminUser],
                                    'delete':[IsAdminUser]}


    def perform_create(self, serializer):
        #print("CourseViewSet.perform_create: request.POST", self.request.POST)
        #print("CourseViewSet.perform_create: request.meta", self.request.META) # could use 'HTTP_REFERER': 'http://127.0.0.1:8000/courses/'
        #print("CourseViewSet.perform_create: request.query_params", self.request.query_params)
        #print('CourseViewSet.perform_create lookup field', self.lookup_field)
        #print("CourseViewSet.perform_create", self.request.data)
        serializer.save(owner=self.request.user)


    # below allows for it to be passed to the template !!!!
    # I AM NOT SURE IF THIS IS OKAY WITH AUTHENTICATION
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        #print("course query_set", queryset)
        page = self.paginate_queryset(queryset)

        ##print(",,",self.filter_backends[0].get_filterset(request,self.get_queryset(),self))
        #for backend in list(self.filter_backends):
            #django_filters.rest_framework.backends.DjangoFilterBackend - https://github.com/carltongibson/django-filter/blob/master/django_filters/rest_framework/backends.py
            ##print("...",backend.filterset_base.form) # <class 'django_filters.rest_framework.filterset.FilterSet'>
            ##print("...1",backend.filterset_base.get_form_class)
            ##print("...1",backend.filterset_base.filters)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            #print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'course_list.html'
                #print("pp",request.get_full_path())
                #print("kwargs",kwargs)
                #print("args",args)

                # https://github.com/encode/django-rest-framework/blob/master/rest_framework/utils/urls.py

                #print('filterfield', CourseFilter.Meta.fields)
                #print('request.query_params', request.query_params.keys())
                response.data = {'results': response.data,'paginator':self.paginator, 'filter':CourseFilter, 'request':request}
            ##print("yeah ok1",response.items())
            ##print("o")
            return response
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            response.template_name = 'course_list.html'
            response.data = {'results': response.data}
        #print("yeah ok2",response.items())
        return response
        """

    def retrieve(self, request, *args, **kwargs):
        #print('CourseViewSet.retrieve lookup field', self.lookup_field)
        response = super(CourseViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            #print("bye george(detail)!\n",response.data)
            course_instance = self.get_object()
            #print("iii",course_instance)
            # okay so at this point none of this is working soe

            # should check if requested and if so get that request obj! is this efficient ??
            if course_instance.requested == True:
                # course detail needs form history

                #NOTE there must be an associated course and if there isnt... we r in trouble!
                request_instance = course_instance.get_request()
                ##print("hfaweuifh ",request_instance)
                this_form = ''#RequestSerializer()
            else:
                # course detail needs to get form
                # URGENT is this creating many copies of the ob?
                this_form = RequestSerializer(data={'course_requested':self.get_object()})
                #print("ok")
                this_form.is_valid()
                print("this_form",this_form.data)
                request_instance =''
            return Response({'course': response.data, 'request_instance':request_instance,'request_form':this_form ,'style':{'template_pack': 'rest_framework/vertical/'}}, template_name='course_detail.html')
        return response


class RequestFilter(filters.FilterSet):
    #activity =
    #filter_fields = ('course_activity','instructors__username','course_schools__abbreviation','course_subjects__abbreviation',) #automatically create a FilterSet class
    # https://github.com/philipn/django-rest-framework-filters/issues/102
    #pls see: https://django-filter.readthedocs.io/en/master/ref/filters.html
    status = filters.ChoiceFilter(choices=Request.REQUEST_PROCESS_CHOICES, field_name='status', label='Status')
    requestor = filters.CharFilter(field_name='owner__username', label='Requestor') # does not include masquerade! and needs validator on input!
    date = filters.DateTimeFilter(field_name='created',label='Created')
    #school = filters.CharFilter(field_name='course_schools__abbreviation',label='School (abbreviation)')
    #subject = filters.CharFilter(field_name='course_subjects__abbreviation', label='Subject (abbreviation)')
    #term = filters.ChoiceFilter(choices=Course.TERM_CHOICES, field_name='course_term', label='Term')
    class Meta:
        model = Request
        fields = ['status','requestor','date']
        #fields = ['activity','instructor','school','subject','term']


class RequestViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions. see http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html

    the function custom permissions handles the ... custom permissions
    """
    # # TODO:
    # [ ] create and test permissions
    # [x] on creation of request instance mutatate course instance so courese.requested = True
    #[ ] ensure POST is only setting masquerade
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    filterset_class = RequestFilter
    search_fields = ['$course_requested__course_name', '$course_requested__course_code',]
    permission_classes = (permissions.IsAuthenticated,)
    #                      IsOwnerOrReadOnly,)
    permission_classes_by_action = {'create': [IsAuthenticated],
                                    'list': [IsAuthenticated],
                                    'retrieve':[IsAuthenticated],
                                    'update':[IsAuthenticated],
                                    'partial_update':[IsAuthenticated],
                                    'delete':[IsAdminUser]}

    def create(self, request, *args, **kwargs):
        """
        functions like a signal
            whenever a request is created this function updates the course instance and updates the crosslisted courses.
        """
        # putting this function inside create because it should only be accessible here.
        # there does not need to be this in the delete of a request...
        def update_course(self,course):
            course.requested = True
            course.save()
            if course.crosslisted:
                for crosslisted in course.crosslisted.all():
                    crosslisted.requested = True
                    crosslisted.request = course.request
                    #print("crosslisted.request , course.request",crosslisted.request , course.request)
                    crosslisted.save()
            #print("-",course.course_code, course.requested)
            #get crosslisted courses
            crosslisted = course.crosslisted
            ##print(crosslisted,"help me!!!")


        """
        Currently this function creates Request instances made from the UI view and the api view
        Therefore there needs to be diambiguation that routes to the UI list view or the api list view
        after creation. Since the POST action is always made to the /api/ endpoint i cannot check what
        the accepted_renderer.format is b/c it will always be api.
            To do this I am tryint to pass a query_param with the UI POST action
            however this may not be the best method perhaps something that has to do with
            sessions would be a better and safer implementation.
        """

        print("views.py in create: request.data", request.data)
        # setting masquerade variable for later use

        try:
            masquerade = request.session['on_behalf_of']
        except KeyError:
            masquerade = ''
        #print("Request create; masqueraded as:", masquerade)

        course = Course.objects.get(course_code=request.data['course_requested'])# get Course instance
        instructors = course.get_instructors()
        #print("course instructors", instructors)

        # CHECK PERMISSIONS custom_permissions(request,request_obj,masquerade,instructors)
        permission = self.custom_permissions(None,masquerade,instructors)
        print("permission, ", permission)


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if not serializer.is_valid():
            #print(serializer.errors)
            # potentially uncomment next line...
            #(serializer.errors)
            messages.add_message(request, messages.ERROR, serializer.errors)
            raise serializers.ValidationError(serializer.errors)

        serializer.validated_data['masquerade'] = masquerade
        print("testing !")
        serializer.validated_data['additional_enrollments'] = None
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # updates the course instance #
        course = Course.objects.get(course_code=request.data['course_requested'])# get Course instance
        update_course(self,course)
        # this allow for the redirect to the UI and not the API endpoint. 'view_type' should be defined in the form that submits this request
        # the following should have redirect pages which say something like "you have created X see item, go back to list"
        if 'view_type' in request.data:
            if request.data['view_type'] == 'UI-course-list':
                return redirect('UI-course-list')
            if request.data['view_type'] == 'UI-request-detail':
                #return Response({'course':course},template_name='request_success.html')
                return redirect('UI-request-detail-success', pk=course.course_code, )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



    def perform_create(self, serializer):
        #print("Request perform_create")
        serializer.save(owner=self.request.user)
        #serializer.save(masquerade="test")# NOTE fix this!


    def list(self, request, *args, **kwargs):
        #print('self.lookup_field', self.lookup_field)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            #print(";",serializer.data)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            #print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'request_list.html'
                #print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator, 'filter': RequestFilter}
            #print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response



    def custom_permissions(self,request_obj,masquerade,instructors):
        """
            This should handle both creating and retrieving
            Keep in mind that instructors can be blank.
            Here 403 errors will be raised
        """

        #print("masquerade: ", masquerade)
        if request_obj:
            pass
            #print("request_obj['masquerade']: ", request_obj['masquerade'])
            #print("request_obj['owner']: ", request_obj['owner'])
        #print("no request_obj: ")
        #print("instructors: ", instructors)

        if self.request.user.is_staff:
            return True

        if self.request.method =="GET":
            # scenario - we are asking to see a request
            # user or masq is in the Request Instance
            # if the user is the owner of the request obj or the listed masquerade
            if not masquerade:
                #print("no masq set")
                if self.request.user.username == request_obj['owner'] or self.request.user.username == request_obj['masquerade']:
                    ##print("")
                    return True
                else:
                    #print("raising error1")
                    raise PermissionDenied({"message":"You don't have permission to access"})
                    return False

            # if the current masquerade is the owner or the masquerade of the request.
            elif masquerade == request_obj['owner'] or masquerade == request_obj['masquerade']:
                return True
            else:
                #print("raising error2")
                raise PermissionDenied({"message":"You don't have permission to access"})
                return False

        if self.request.method =="POST":
            # scenario - we are asking to create a request from a course, request_obj=None
            if instructors: # there are instructors
                #print("we have intsructors")
                if self.request.user.username in instructors:
                    #print("self.request.user.username in instructors: ", self.request.user.username, "in ", instructors, "==",self.request.user.username in instructors)
                    #("masquerade in instructors: ", masquerade," in ", instructors, "== ", masquerade in instructors)
                    return True
                elif masquerade and masquerade in instructors:
                    return True
                else:
                    #print("raising error3")
                    raise PermissionDenied({"message":"You don't have permission to access"})
                    return False
            # no instructors then anyone can create a request for it
            else:
                #print("no instructors then anyone can create a request for it")
                return True
        else:
            #print("OHH BUDY WE HAVE A PROBLEM")
            return False

    def check_request_update_permissions(request,response_data):
        request_status = response_data['status']
        request_owner = response_data['owner']
        request_masquerade = response_data['masquerade'] #
        print("request_masquerade",request_masquerade)
            # owner is also considered masquerade
        if request_status == "SUBMITTED": permissions = {'staff':['lock','cancel','edit'],'owner':['cancel','edit']}
        elif request_status == "APPROVED": permissions = {'staff':['cancel','edit','lock','create'],'owner':['cancel']}
        elif request_status == "LOCKED": permissions = {'staff':['cancel','edit','unlock'],'owner':['']}
        elif request_status == "CANCELED": permissions = {'staff':['lock'],'owner':['']}
        elif request_status == "IN_PROCESS": permissions = {'staff':['lock'],'owner':['']}
        elif request_status == "COMPLETED": permissions = {'staff':[''],'owner':['']}
        else: permissions = {'staff':[''],'owner':['']} # throw error!???

        # permission - 'create' pushes the request into the in_process queue
        # permission - 'unlock' sets it as submitted again

        if request.session['on_behalf_of']:
            # you have you're masq set
            current_masquerade = request.session['on_behalf_of']
            print("request.session['on_behalf_of']",request.session['on_behalf_of'])
            if current_masquerade == request_owner:
                return permissions['owner']

        #else:
        if request.user.is_staff:
            return permissions['staff']

        # they own or was submitted on their behalf
        if request.user.username == request_owner or (request.user.username == request_masquerade and request_masquerade !=''):
            #print("yeahh buddy",request.user.username)
            return permissions['owner']
        #
        return ''



    def retrieve(self, request, *args, **kwargs):
        """
            can retrieve for /requests/<COURSE_CODE>/ or /requests/<COURSE_CODE/edit
        """
        #print("ok in retrieve self,,",self.request.session.get('on_behalf_of','None'))
        #print("ok in ret,,", request.session.get('on_behalf_of','None'))
        #print("Request.retrieve")
        #print("request.data",request.data)
        #print("request.resolver_match.url_name",request.resolver_match.url_name)


        response = super(RequestViewSet, self).retrieve(request, *args, **kwargs)
        #print("response",response.data)
        if request.resolver_match.url_name == "UI-request-detail-success":
            return Response({'request_instance': response.data}, template_name='request_success.html')

        # CHECK PERMISSIONS custom_permissions(request_obj, current_masquerade,instructors)
        obj_permission = self.custom_permissions(response.data,request.session.get('on_behalf_of','None'),response.data['course_info']['instructors'])
        #print("permission, ", obj_permission)

        if request.accepted_renderer.format == 'html':
            print("bye george(UI-request-detail)!\n",response.data)
            permissions = RequestViewSet.check_request_update_permissions(request, response.data)
            print("request permissions",permissions)
            if request.resolver_match.url_name == "UI-request-detail-edit":
            #if 'edit' in request.path.split('/') : # this is possibly the most unreliable code ive ever written
                # we want the edit form
                # CHECK PERMISSIONS -> must be creator and not be masquerading as creator
                # CHECK IF request status is submitted ( for requestor ) or submitted/locked( for admin)
                ##print("object",self.get_object())
                here= RequestSerializer(self.get_object(), context={'request':request})

                ##print(here.title_override)
                ##print("RequestSerializer(response.data)",here)
                print("request_form", here,here.data)
                return Response({'request_instance': response.data,'permissions':permissions,'request_form':here,'style':{'template_pack': 'rest_framework/vertical/'}}, template_name='request_detail_edit.html') #data={'course_requested':response.data['course_requested']},partial_update=True
            return Response({'request_instance': response.data, 'permissions':permissions}, template_name='request_detail.html')
        return response

    def destroy(self, request, *args, **kwargs):
        #print("OH MY GOLLY GEEE we r deleteing a request")
        instance = self.get_object()
        # Must get Course and set .request to true
        course = Course.objects.get(course_code=instance.course_requested)# get Course instance
        course.requested = False
        course.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated()
        #need to check if the post is for masquerade
        # '' is different than None ... if the key isnt present the .get() returns None
        """
        if request.data.get('on_behalf_of')=='':
            #print(request.get_full_path())
            #print("ok self,,",self.request.session.get('on_behalf_of','None'))
            #print("ok no self,,",request.session.get('on_behalf_of','None'))
            set_session(request)
            return redirect(request.get_full_path())
        """

    def update(self, request, *args, **kwargs):
        #print("in update")

        partial = kwargs.pop('partial', False)#see if partial
        instance = self.get_object() # get request to update
        additional_enrollments_partial = html.parse_html_list(request.data, prefix ='additional_enrollments')
        print("request.data, data to update!",request.data, additional_enrollments_partial)
        d = request.data.dict()
        #test1 = json.dumps({k: d.getlist(k) for k in d.keys() if not k.startswith('additional_enrollments')})
        #test2 = json.dumps({k: ",".join(d.getlist(k)) for k in d.keys()})
        #ad = additional_enrollments_partial
        #test3 = json.dumps({k: (ad.getlist(k) if len(ad.getlist(k)) > 1 else ad[k]) for k in ad.keys()})

        #print("test1",test1)
        #print("test2",test2)
        #print("test3",test3)
        # check if we are updating
        if additional_enrollments_partial:
            print("we are just updating the additional_enrollments", additional_enrollments_partial)
            print("partialll",partial)
            ok= additional_enrollments_partial[0].dict()
            print("ok",ok)

            # removing spaces from keys
            # storing them in sam dictionary
            ok = {x.replace('[', '').replace(']',''): v
                for x, v in ok.items()}
            print("newok",ok)
            #qdict.update({'additional_enrollments':additional_enrollments_partial[0]})
            final_add_enroll = []
            #for k in additional_enrollments_partial:
            for add in additional_enrollments_partial:
                add = add.dict()
                new_add = {x.replace('[', '').replace(']',''): v
                    for x, v in add.items()}
                print("newadd",new_add)
                if '' in new_add.values():
                    pass
                else:
                    final_add_enroll +=[new_add]
            print("final_add_enroll",final_add_enroll)
            #print(additional_enrollments_partial.dict())
            d['additional_enrollments']=final_add_enroll#[{'user':'molly','role':'DES'}]})
            #print("test1.2", test1)
#            qdict.update({'additional_enrollments':{'user':'molly','role':'TA'}})
            #qdict.update(test1)
            print("d",d,"reqiest.data",request.data)
            #request.data = qdict
            serializer = self.get_serializer(instance, data=d, partial=partial)
            print(serializer.initial_data)
            #request.data['additional_enrollments'] = additional_enrollments_partial
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        print("about to check if serializer is valid")
        serializer.is_valid()#raise_exception=True)
        if not serializer.is_valid():
            messages.add_message(request, messages.ERROR, "An error occurred: Please add the Content Copy information to the additional instructions field and a Courseware Support team memeber will assist you.")
            raise serializers.ValidationError(serializer.errors)

        self.perform_update(serializer)
        #print(":^) !")
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        #Lets check if we need to send an email?
        if 'status' in request.data:
            if request.data['status'] =='LOCKED':
                #lets send that email babie !!!!
                email_processor.admin_lock(context={'request_detail_url':request.build_absolute_uri(reverse('UI-request-detail',kwargs={'pk':request.data['course_requested']})) , 'course_code': request.data['course_requested']})

        if 'view_type' in request.data:
            if request.data['view_type'] == 'UI-request-detail':
                #print("LLL")
                permissions = RequestViewSet.check_request_update_permissions(request, {'owner':instance.owner,'masquerade':instance.masquerade,'status':instance.status})
                return Response({'request_instance':serializer.data,'permissions':permissions}, template_name='request_detail.html')
                #return redirect('UI-request-detail', pk=request.data['course_requested'])

        return Response(serializer.data)


class UserViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions. (READONLY)
    """
    # only admins ( user.is_staff ) can do anything with this data
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    #filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('profile__penn_id',)
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retrieve':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

    """
    # this is just to havet the pk be username and not id
    def retrieve(self, request, pk=None):
        #print("IM DOING MY BEST")
        instance = User.objects.filter(username=pk)
        #print(instance)


        serializer = self.get_serializer(instance)
        return Response(serializer.data)

        return Response(serializer.data)
    """




class SchoolViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    This viewset only provides custom `list` actions
    """
    # # TODO:
    #[ ] ensure POST is only setting masquerade
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retrieve':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

#    def perform_create(self, serializer):
#        serializer.save(owner=self.request.user)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        #print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            #print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'schools_list.html'
                #print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator}
            #print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            #print("template_name",response.template_name)
            response.template_name = 'schools_list.html'
            #print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response
        """

    def post(self, request,*args, **kwargs):
        #print("posting")
        #if request.user.is_authenticated():

        """
        #need to check if the post is for masquerade
        #print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))
        """

    def update(self, request, *args, **kwargs):
        #print("update?")
        #print("args",args)
        #print("kwargs", kwargs)
        #print("request.data", request.data)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        if request.data.get('view_type',None) == 'UI':
            pass
            #print("its happening")

        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        #print("this is dumb",request.method)
        #print("self.lookup_field: ",self.lookup_field)
        # this response should probably be paginated but thats a lot of work ..
        response = super(SchoolViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            ##print("bye george(UI-request-detail)!\n",response.data)
            return Response({'data': response.data}, template_name='school_detail.html')
        return response


class SubjectViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    This viewset only provides custom `list` actions
    """
    # # TODO:
    #[ ] ensure POST is only setting masquerade

    #lookup_field = 'abbreviation'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retrieve':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}
#    def perform_create(self, serializer):
#        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        #print("request.data", request.data)
        serializer = self.get_serializer(data=request.data)
        #print("serializer",serializer)
        serializer.is_valid(raise_exception=True)
        #print("ok")
        self.perform_create(serializer)
        #print("ok2")
        headers = self.get_success_headers(serializer.data)
        #print("serializer.data",serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def list(self, request, *args, **kwargs):
        #print("in list")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        #print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            #print("template_name",response.template_name)

            if request.accepted_renderer.format == 'html':
                response.template_name = 'subjects_list.html'
                response.data = {'results': response.data,'paginator':self.paginator}
            return response
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            #print("template_name",response.template_name)
            response.template_name = 'subjects_list.html'
            #print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response
        """

    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated():

        """
        #need to check if the post is for masquerade
        #print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))
        """

    def retrieve(self, request, *args, **kwargs):
        #print("request.data",request.data)
        response = super(SubjectViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            ##print("bye george(UI-request-detail)!\n",response.data)
            return Response({'data': response.data}, template_name='subject_detail.html')
        return response




class NoticeViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    THIS IS A TEMPORARY COPY
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retrieve':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}
    def perform_create(self, serializer):
        #print("NoticeViewSet - perform_create trying to create Notice")
        ##print(self.request.user) == username making request
        serializer.save(owner=self.request.user)


class HomePage(APIView):#,
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home_content.html'
    login_url = '/accounts/login/'
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retrieve':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # # TODO:
        # [ ] Check that valid pennkey
        # [ ] handles if there are no notice instances in the db
        #print("request.user",request.user)
        #print("in home")
        try:
            notice = Notice.objects.latest()
            #print(Notice.notice_text)
        except Notice.DoesNotExist:
            notice = None
            #print("no notices")

        # this should get the courses from this term !
        # currently we are just getting the courses that have not been requested
        masquerade = request.session['on_behalf_of']
        if masquerade:
            user = User.objects.get(username=masquerade)
        else:
            user = request.user

        courses= Course.objects.filter(instructors=user)
        courses_count = courses.count()
        courses = courses[:15] #requested=False
        #print(courses)
        #print("1",user,"2",user.username)
        site_requests = Request.objects.filter(Q(owner=user) | Q(masquerade=user))
        site_requests_count = site_requests.count()
        site_requests= site_requests[:15]

        ##print(site_requests, site_requests[0].course_requested.course_name)
        # for courses do instructors.courses since there is a manytomany relationship
        return Response({'data':
            {'notice':notice,
            'site_requests':site_requests,
            'site_requests_count':site_requests_count,
            'srs_courses': courses,
            'srs_courses_count': courses_count,
            'username':request.user}})

    # get the user id and then do three queries to create these tables
    # you should get the user id of the auth.user or if they are masquerading get the id of that user
    # 1. Site Requests
    # 2. SRS Courses
    # 3. Canvas Sites

#    def post(self, request,*args, **kwargs):
#        return redirect(request.path)


    def set_session(request):
        print("set_session request.data",request.data)
        try:
            on_behalf_of = request.data['on_behalf_of']
            print("found on_behalf_of in request.data ", on_behalf_of)
            if on_behalf_of: # if its not none -> if exists then see if pennkey works
                lookup_user = utils.validate_pennkey(on_behalf_of)
                if lookup_user == None: #if pennkey is good the user exists
                    print("not valid input")
                    messages.error(request,'Invalid Pennkey -- Pennkey must be Upenn Employee')
                    on_behalf_of = None
                elif lookup_user.is_staff == True:
                    messages.error(request,'Invalid Pennkey -- Pennkey cannot be Courseware Team Member')
                    on_behalf_of = None

        except KeyError:
            pass
        # check if user is in the system
        request.session['on_behalf_of'] = on_behalf_of
        #print("masquerading as:", request.session['on_behalf_of'])

    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated():
        #need to check if the post is for masquerade
        #print("posting in home")
        #print("\trequest.get_full_path()",request.get_full_path())
        #print("\trequest.META[''HTTP_REFERER'']",request.META['HTTP_REFERER'])
        HomePage.set_session(request)
        return(redirect(request.META['HTTP_REFERER']))


class AutoAddViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    provides list create and destroy actions only
    no update or detail actions.
    """

    queryset = AutoAdd.objects.all()
    serializer_class = AutoAddSerializer
    permission_classes_by_action = {'create': [IsAdminUser],
                                    'list': [IsAdminUser],
                                    'retrieve':[IsAdminUser],
                                    'update':[IsAdminUser],
                                    'partial_update':[IsAdminUser],
                                    'delete':[IsAdminUser]}

    def create(self, request, *args, **kwargs):
        #print(self.request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        #print("headers",headers)
        #print("autoadd data",serializer.data) # {'url': 'http://127.0.0.1:8000/api/autoadds/1/', 'user': 'username_8', 'school': 'AN', 'subject': 'abbr_2', 'id': 1, 'role': 'ta'}
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        email_processor.autoadd_contact({'user':serializer.data['user'], 'role':serializer.data['role'], 'school':School.objects.get(abbreviation=serializer.data['school']).name, 'subject':Subject.objects.get(abbreviation=serializer.data['subject']).name})
        #print("got here")
        if request.accepted_renderer.format == 'html':
            response.template_name = 'admin/autoadd_list.html'
            return(redirect('UI-autoadd-list'))
        return response


    def list(self, request, *args, **kwargs):
        ##print(request.user.is_authenticated())
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        #print("1")

        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            #print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'admin/autoadd_list.html'
                #print("template_name",response.template_name)
                #print("qqq",repr(AutoAddSerializer))
                #print("qqqq",AutoAddSerializer.fields)
                response.data = {'results': response.data,'paginator':self.paginator,'serializer':AutoAddSerializer}
            #print("request.accepted_renderer.format",request.accepted_renderer.format)
            #print("yeah ok1",response.items())
            return response

    def destroy(self, request, *args, **kwargs):
        #print("ss")
        instance = self.get_object()
        self.perform_destroy(instance)
        #print("ok", request.path)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        if 'UI' in request.data:
            if request.data['UI'] == 'true':

                response.template_name = 'admin/autoadd_list.html'
                return(redirect('UI-autoadd-list'))
        return response





class UpdateLogViewSet(MixedPermissionModelViewSet,viewsets.ModelViewSet):
    """
    THIS IS A TEMPORARY COPY
    This viewset automatically provides `list` and `detail` actions.
    """
    #permission_classes = (IsAdminUser,)
    queryset = UpdateLog.objects.all()
    serializer_class = UpdateLogSerializer
    permission_classes_by_action = {'create': [IsAdminUser],
                                    'list': [IsAdminUser],
                                    'retrieve':[IsAdminUser],
                                    'update':[IsAdminUser],
                                    'partial_update':[IsAdminUser],
                                    'delete':[IsAdminUser]}
    # CHECK PERMISSIONS!
    def list(self, request, *args, **kwargs):
        #print("yeah ok")
        # see more about the models here https://django-celery-beat.readthedocs.io/en/latest/index.html
        #https://medium.com/the-andela-way/crontabs-in-celery-d779a8eb4cf
        periodic_tasks = PeriodicTask.objects.all()
        return Response({'data': periodic_tasks}, template_name='admin/log_list.html')


# --------------- USERINFO view -------------------

#@login_required(login_url='/accounts/login/')
def userinfo(request):
    form = EmailChangeForm(request.user)
    #print(request.method)
    if request.method=='POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('userinfo') # this should redirect to success page
    return render(request, "user_info.html", {'form':form})

# --------------- CONTACT view -------------------
# add to your views
def contact(request):
    form_class = ContactForm
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            contact_name = request.POST.get('contact_name', '')
            contact_email = request.POST.get('contact_email', '')
            form_content = request.POST.get('content', '')

            # Email the profile with the
            # contact information
            context = {'contact_name': contact_name,'contact_email': contact_email,'form_content': form_content,}
            email_processor.feedback(context)
            return redirect('contact')
    return render(request, 'contact.html', {'form': form_class,})


# --------------- Temporary Email view -------------------
"""
This view is only for beta testing of the app
"""
import os
from os import listdir
def temporary_email_list(request):
    filelist = os.listdir('course/static/emails/')
    return render(request, 'email/email_log.html', {'filelist':filelist})

from django.http import HttpResponse
def my_email(request,value):
    email = open("course/static/emails/"+value, "rb").read()
    return render(request, 'email/email_detail.html', {'email':email.decode("utf-8")} )


#SEE MORE: https://docs.djangoproject.com/en/2.1/topics/email/
