from django.shortcuts import render
from django_registration.backends.one_step.views import RegistrationView as BaseRegistrationView

# Create your views here.

class RegistrationView(BaseRegistrationView):
    success_url = '/'