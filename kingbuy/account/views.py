from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from django.utils.translation import pgettext, gettext_lazy as _

from .forms import (
    LoginForm,
)
from .models import User

def login(request):
    kwargs = {"template_name": "account/login.html", "authentication_form": LoginForm}
    return django_views.LoginView.as_view(**kwargs)(request, **kwargs)


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, _("You have been successfully logged out."))
    return redirect(settings.LOGIN_REDIRECT_URL)
