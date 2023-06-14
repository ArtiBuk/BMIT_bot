from django.urls import path
from .views import create_user, view_users

urlpatterns = [
    path('users/', create_user, name='create_user'),
    path('users/view/', view_users, name='view_users'),
]
