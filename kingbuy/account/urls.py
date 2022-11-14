from django.urls import path, re_path
from django.contrib.auth import views as django_views
from . import views

app_name = 'account'

urlpatterns = [
    re_path( r"^login/$", views.KingbuyLoginView.as_view(), name="login" ),
    re_path( r"^logout/$", views.logout, name="logout" ),
    ]
