from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post


def home(request):
    if not request.user.is_authenticated:
        return render(request, "posts/landing.html")
    posts = (
        Post.objects.select_related("author", "author__profile")
        .prefetch_related("comments", "likes")
        .annotate(likes_count=Count("likes"))
    )
    return render(request, "posts/home.html", {"posts": posts})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "author__profile").annotate(
            likes_count=Count("likes")
        ),
        id=post_id,
    )
    comments = post.comments.select_related("author", "author__profile")
    form = CommentForm()
    return render(
        request,
        "posts/post_detail.html",
        {"post": post, "comments": comments, "form": form},
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form, "mode": "create"})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form, "mode": "edit"})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect("home")
    return render(request, "posts/post_confirm_delete.html", {"post": post})


@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect("post_detail", post_id=post.id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post_id = comment.post_id
    if request.method == "POST":
        comment.delete()
    return redirect("post_detail", post_id=post_id)


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))

# Create your views here.
