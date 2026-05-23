from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("posts/<int:post_id>/comment/", views.comment_create, name="comment_create"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("posts/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("posts/<int:post_id>/visibility/<str:visibility>/", views.set_visibility, name="set_visibility"),
    path("posts/<int:post_id>/react/<str:kind>/", views.add_reaction, name="add_reaction"),
]
