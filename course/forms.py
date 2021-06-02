from dal import autocomplete
from django import forms
from django.contrib.auth.models import User

from course.models import AdditionalEnrollment, CanvasSite, Subject


# our new form
class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)


class UserForm(forms.ModelForm):
    # please only use this when you need to auto complete on the name field !
    username = forms.ModelChoiceField(
        label="user",
        queryset=User.objects.all(),
        # required=False,
        widget=autocomplete.ModelSelect2(url="user-autocomplete"),
    )

    class Meta:
        model = User
        fields = "__all__"


class SubjectForm(forms.ModelForm):
    # please only use this when you need to auto complete on the name field !
    abbreviation = forms.ModelChoiceField(
        label="Abbreviation",
        queryset=Subject.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url="subject-autocomplete"),
    )

    class Meta:
        model = Subject
        fields = "__all__"


class CanvasSiteForm(forms.ModelForm):
    # please only use this when you need to auto complete on the name field !
    name = forms.ModelChoiceField(
        label="content_copy",
        queryset=CanvasSite.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url="canvas_site-autocomplete"),
    )

    class Meta:
        model = CanvasSite
        fields = "__all__"


class EmailChangeForm(forms.Form):
    """
    A form that lets a user change set their email while checking for a change in the
    e-mail.
    """

    error_messages = {
        "email_mismatch": ("The two email addresses fields didn't match."),
        "not_changed": ("The email address is the same as the one already defined."),
    }

    new_email1 = forms.EmailField(
        label=("New email address"),
        widget=forms.EmailInput,
    )

    new_email2 = forms.EmailField(
        label=("New email address confirmation"),
        widget=forms.EmailInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        # print(self.user)
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self):
        old_email = self.user.email
        new_email1 = self.cleaned_data.get("new_email1")
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages["not_changed"],
                    code="not_changed",
                )
        return new_email1

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get("new_email1")
        new_email2 = self.cleaned_data.get("new_email2")
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                # print("yeahgggggg")
                raise forms.ValidationError(
                    self.error_messages["email_mismatch"],
                    code="email_mismatch",
                )
        return new_email2

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user
