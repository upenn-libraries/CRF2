from django import template
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.encoding import iri_to_uri
from django.utils.html import escape
from rest_framework.utils.urls import remove_query_param

from course.models import *

register = template.Library()


@register.simple_tag
def delete_query_param(request, key):
    """
    Add a query parameter to the current request url, and return the new url.
    """

    iri = request.get_full_path()
    uri = iri_to_uri(iri)
    val = remove_query_param(uri, key)
    return escape(val)


@register.simple_tag
def get_item(qp, key):
    # qp is request.query_params
    # print("qp", qp)
    # print("key, val", (key , val))
    if val == None:
        return ""
    else:
        return val


@register.simple_tag
def get_user(user):
    # qp is request.query_params
    # print(user)
    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        user = None
    else:
        return user


@register.simple_tag
def masquerading(request):
    if request.session["on_behalf_of"]:
        return True
    return False


@register.simple_tag
def filter_messages(messages, type):
    answer = []
    if messages:
        # print("u",messages)
        for message in messages:
            if message.tags == type:
                # print(message.tags)
                answer += [message]
    return answer


@register.filter
def coursecodetoString(coursecode):
    middle = coursecode[:-5][4:]
    return "%s-%s-%s %s" % (coursecode[:-11], middle[:3], middle[3:], coursecode[-5:])


@register.filter
def asrepr(course):
    term = course["year"] + course["course_term"]
    # print(course['course_section'])

    return "%s-%s-%s %s" % (
        course["course_subject"],
        course["course_number"],
        course["course_section"],
        term,
    )
    # -".join([])


@register.simple_tag
def get_markdown(location):
    if PageContent.objects.filter(location=location).exists():
        page = PageContent.objects.get(location=location)
        return page.get_page_as_markdown()
    return ""


@register.simple_tag
def get_markdown_id(location):
    if PageContent.objects.filter(location=location).exists():
        page = PageContent.objects.get(location=location)
        return page.pk
    return ""


@register.filter("mytruncate_chars")
def truncate_chars(value, max_length):
    if len(value) > max_length:
        truncd_val = value[:max_length]
        if not len(value) == max_length + 1 and value[max_length + 1] != " ":
            truncd_val = truncd_val[: truncd_val.rfind(" ")]
        return truncd_val
    return value


"""
@register.simple_tag
def add_query_param(request, key, val):

    #Add a query parameter to the current request url, and return the new url.

    iri = request.get_full_path()
    uri = iri_to_uri(iri)
    return escape(replace_query_param(uri, key, val))



def replace_query_param(url, key, val):

    ##Given a URL and a key/val pair, set or replace an item in the query
    ##parameters of the URL, and return the new URL.

    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):

    ##Given a URL and a key/val pair, remove an item in the query
    ##parameters of the URL, and return the new URL.

    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))



"""
