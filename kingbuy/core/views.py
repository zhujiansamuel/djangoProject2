from django.contrib.admin.views.decorators import (
    staff_member_required as _staff_member_required,
    user_passes_test,
)
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.template.response import TemplateResponse

def staff_member_required(f):
    return _staff_member_required(f, login_url="account:login")


def superuser_required(
    view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="account:login"
):
    """Check if the user is logged in and is a superuser.

    Otherwise redirects to the login page.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


@staff_member_required
def index(request):
    ctx = {

    }
    return TemplateResponse(request, "index.html", ctx)
