from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('add/', views.create_user),
    path('search/', views.get_users),
    re_path(r'search/(?P<user_id>[0-9a-f-]+)/', views.get_users),
]