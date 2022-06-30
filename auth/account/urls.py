from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('add/', views.create_user),
    path('search/', views.get_users),
    # TODO: search specific user id data
]