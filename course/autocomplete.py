from dal import autocomplete
from course.models import Subject, CanvasSite
from django.contrib.auth.models import User
from django.db.models import Q


# https://django-autocomplete-light.readthedocs.io/en/master/


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        print("self.request.user.is_authenticated", self.request.user.is_authenticated)
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()
        if self.q:
            # lets limit it to only the first 8 matches
            qs = qs.filter(username__istartswith=self.q)[:8]
        else:
            # dont show all of them if there is nothing there
            return User.objects.none()
        return qs

    def get_result_value(self, result):
        """
        this below is the default behavior,
        change it to whatever you want returned
        """
        return str(result.username)


class SubjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # print("self.request.user.is_authenticated",self.request.user.is_authenticated)
        if not self.request.user.is_authenticated:
            return Subject.objects.none()

        qs = Subject.objects.all()
        if self.q:
            # lets limit it to only the first 8 matches
            qs = qs.filter(abbreviation__istartswith=self.q)[:8]
        else:
            # dont show all of them if there is nothing there
            return Subject.objects.none()
        return qs

    def get_result_value(self, result):
        """
        this below is the default behavior,
        change it to whatever you want returned
        """
        # self.name, self.abbreviation
        return str(result.abbreviation)  # + "("+str(result.name)+")"


class CanvasSiteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        print("self.request.user.is_authenticated", self.request.user.is_authenticated)
        if not self.request.user.is_authenticated:
            return CanvasSite.objects.none()

        masquerade = self.request.session["on_behalf_of"]
        if masquerade:
            qs = CanvasSite.objects.filter(
                Q(owners=User.objects.get(username=masquerade))
                | Q(added_permissions=self.request.user)
            )
        else:
            qs = CanvasSite.objects.filter(
                Q(owners=self.request.user) | Q(added_permissions=self.request.user)
            )
        if self.q:
            # lets limit it to only the first 8 matches
            qs = qs.filter(name__istartswith=self.q)[:8]
        else:
            # dont show all of them if there is nothing there
            return qs  # CanvasSite.objects.none()
        return qs

    def get_result_value(self, result):
        """
        this below is the default behavior,
        change it to whatever you want returned
        """

        # self.name, self.abbreviation
        return str(result.canvas_id)  # + "("+str(result.name)+")"


# should have this for subjects,  and potentially content copies
