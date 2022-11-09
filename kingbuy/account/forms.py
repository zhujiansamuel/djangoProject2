from django import forms
from django.conf import settings
from django.contrib.auth import forms as django_forms, update_session_auth_hash
from django.utils.translation import pgettext, pgettext_lazy



class LoginForm(django_forms.AuthenticationForm):
    username = forms.EmailField(label=pgettext("Form field", "Email"), max_length=75)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        if request:
            email = request.GET.get("email")
            if email:
                self.fields["username"].initial = email
