from rest_framework import generics, permissions
from django.contrib.auth.models import User


"""
I've been running into issues with the no. of SQL queries used in each page.. so in an attempt to reduce that
I am passing the staff status as a variable to all pages ... since its essentially used in all pages... 

"""

# The context processor function
def user_permissons(request):
    value = request.user.is_staff

    return {
        "staff": value,
    }
