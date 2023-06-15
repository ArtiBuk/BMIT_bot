from django.urls import path
from .views import create_user, view_users, create_report, view_report

urlpatterns = [
    path("users/", create_user, name="create_user"),
    path("users/view/", view_users, name="view_users"),
    path("reports/", create_report, name="create_report"),
    path("reports/view/", view_report, name="view_report"),
]
