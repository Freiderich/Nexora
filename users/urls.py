from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile, name="profile"),
]
