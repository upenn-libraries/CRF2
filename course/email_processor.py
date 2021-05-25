from django.template.loader import get_template
from course.forms import ContactForm, EmailChangeForm
from django.core.mail import EmailMessage
from course.models import *
import logging


"""
Types of emails being sent:
1    added_to_request.txt
        PARAMS: user, role, course_code, request_detail_url
2    autoadd_contact.txt
        PARAMS: user, role, school, subject
3    request_submitted.txt
        PARAMS: requestor, course_code, request_detail_url
4    request_submitted_onbehalf.txt
        PARAMS: requestor, masquerade, course_code, request_detail_url
5    admin_lock.txt
        PARAMS: request_detail_url, course_code
6    course_created_canvas.txt
        PARAMS: requestor , instructors, course_code, canvas_url, request_detail_url
7    feedback.txt
        PARAMS: contact_name, contact_email, form_content

note any reference to user's (user, requestor, masquerade) should be a string of their pennkey and then the function get_email
will look up thier email in the system.

"""


def get_email(pennkey):
    try:
        user_email = User.objects.get(username=pennkey).email
        if user_email == "":
            user_email = "None"
            # alert some process ?
        print("found %s email for %s" % (user_email, pennkey))
    except User.DoesNotExist:
        user_email = ""
        logging.critical("could not find %s user in system" % (pennkey))
    return user_email


# IMPLEMENTED
# sent when the contact form is filled out
def feedback(context):
    template = get_template("email/feedback.txt")
    # context = {'contact_name':data['contact_name'], 'contact_email':data['contact_email'], 'form_content':data['form_content']}
    content = template.render(context)
    email = EmailMessage(
        subject="CRF Feedback from " + context["contact_name"],
        body=content,
        to=["mfhodges@upenn.edu"],
    )
    email.send()


# sent when the manager has created the request in canvas
def course_created_canvas(context):
    template = get_template("email/course_created_canvas.txt")
    content = template.render(context)
    email = EmailMessage(
        subject="CRF Notification: Course Request Completed ("
        + context["course_code"]
        + ")",
        body=content,
        to=list(map(lambda x: get_email(x), listcontext["instructors"]))
        + get_email(context["requestor"]),
    )
    email.send()


# IMPLEMENTED
# sent when a request is locked ( either by manager or in the UI)
def admin_lock(context):
    template = get_template("email/admin_lock.txt")
    content = template.render(context)
    email = EmailMessage(
        subject="CRF notification locked request",
        body=content,
        to=["mfhodges@upenn.edu"],  # add molly and joe ?
    )
    email.send()


# sent when a request is created while the user is masquerading
def request_submitted_onbehalf(context):
    template = get_template("email/request_submitted_onbehalf.txt")
    # context = {'contact_name':data['contact_name'], 'contact_email':data['contact_email'], 'form_content':data['form_content']}
    content = template.render(context)
    email = EmailMessage(
        subject="CRF Notification: Course Request (" + context["course_code"] + ")",
        cc=[context["requestor"]],
        body=content,
        to=[get_email(context["masquerade"])],
    )
    email.send()


# sent when a request is submitted when the user is NOT masquerading
def request_submitted(context):
    template = get_template("email/request_submitted.txt")
    # context = {'contact_name':data['contact_name'], 'contact_email':data['contact_email'], 'form_content':data['form_content']}
    content = template.render(context)
    email = EmailMessage(
        subject="CRF Notification: Course Request (" + context["course_code"] + ")",
        body=content,
        to=[get_email(context["requestor"])],
    )
    email.send()


# IMPLEMENTED
# sent when autoadd contact object is created in UI ( not in admiin )
def autoadd_contact(context):
    template = get_template("email/autoadd_contact.txt")
    # context = {'contact_name':data['contact_name'], 'contact_email':data['contact_email'], 'form_content':data['form_content']}
    content = template.render(context)
    email = EmailMessage(
        subject="CRF Notification: Added as Auto-Add Contact",
        body=content,
        to=[get_email(context["user"])],
    )
    email.send()


# sent when a request is created and there has been custom adds
def added_to_request(context):
    template = get_template("email/added_to_request.txt")
    # context = {'contact_name':data['contact_name'], 'contact_email':data['contact_email'], 'form_content':data['form_content']}
    content = template.render(context)
    email = EmailMessage(
        subject="CRF Notification: Added to Course Request",
        body=content,
        to=[get_email(context["user"])],
    )
    email.send()


def main():
    logging.basicConfig(
        filename="course/static/logs/emails.log", format="%(asctime)s %(message)s"
    )
