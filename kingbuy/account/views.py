from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from django.utils.translation import pgettext, gettext_lazy as _
from django.urls import reverse

from .forms import (
    LoginForm,
)
from .models import User

# def login(request):
#     kwargs = {"template_name": "account/login.html", "authentication_form": LoginForm}
#     return django_views.LoginView.as_view(**kwargs)(request, **kwargs)

class KingbuyLoginView(django_views.LoginView):
    form_class = LoginForm
    template_name = 'account/login.html'
    next_page = 'index'

    def get_success_url(self):
        return reverse('index')


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, _("You have been successfully logged out."))
    return redirect(settings.LOGIN_REDIRECT_URL)
