from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, RegisterForm
from posts.models import Post


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related("author", "author__profile").prefetch_related("comments", "likes")
    if request.user != user:
        posts = posts.exclude(visibility=Post.VISIBILITY_PRIVATE)
    posts = posts.annotate(
        likes_count=Count("likes"),
        reactions_count=Count("reactions"),
        reaction_love_count=Count("reactions", filter=Q(reactions__kind="love")),
        reaction_laugh_count=Count("reactions", filter=Q(reactions__kind="laugh")),
        reaction_wow_count=Count("reactions", filter=Q(reactions__kind="wow")),
        reaction_sad_count=Count("reactions", filter=Q(reactions__kind="sad")),
        reaction_fire_count=Count("reactions", filter=Q(reactions__kind="fire")),
    )
    return render(request, "users/profile.html", {"profile_user": user, "posts": posts})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "users/edit_profile.html", {"form": form})

# Create your views here.
