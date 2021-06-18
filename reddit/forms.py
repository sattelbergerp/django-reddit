from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import User
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Account'))
        self.fields[User.get_email_field_name()].required = False
        self.fields[User.get_email_field_name()].help_text = 'Optional. Used to reset your password if you lose it.'

class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Login'))
