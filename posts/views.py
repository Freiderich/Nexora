from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post, Reaction


def _post_reaction_payload(post):
    stats = post.reactions.aggregate(
        reaction_love_count=Count("id", filter=Q(kind="love")),
        reaction_laugh_count=Count("id", filter=Q(kind="laugh")),
        reaction_wow_count=Count("id", filter=Q(kind="wow")),
        reaction_sad_count=Count("id", filter=Q(kind="sad")),
        reaction_fire_count=Count("id", filter=Q(kind="fire")),
        reactions_count=Count("id"),
    )
    return {
        **stats,
        "likes_count": post.likes.count(),
    }


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def home(request):
    if not request.user.is_authenticated:
        return render(request, "posts/landing.html")
    comment_qs = Comment.objects.select_related("author", "author__profile")
    posts = (
        Post.objects.select_related("author", "author__profile")
        .prefetch_related(Prefetch("comments", queryset=comment_qs), "likes")
        .exclude(visibility=Post.VISIBILITY_PRIVATE)
        .annotate(
            likes_count=Count("likes"),
            reactions_count=Count("reactions"),
            reaction_love_count=Count("reactions", filter=Q(reactions__kind="love")),
            reaction_laugh_count=Count("reactions", filter=Q(reactions__kind="laugh")),
            reaction_wow_count=Count("reactions", filter=Q(reactions__kind="wow")),
            reaction_sad_count=Count("reactions", filter=Q(reactions__kind="sad")),
            reaction_fire_count=Count("reactions", filter=Q(reactions__kind="fire")),
        )
    )
    return render(request, "posts/home.html", {"posts": posts})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "author__profile").annotate(
            likes_count=Count("likes"),
            reactions_count=Count("reactions"),
            reaction_love_count=Count("reactions", filter=Q(reactions__kind="love")),
            reaction_laugh_count=Count("reactions", filter=Q(reactions__kind="laugh")),
            reaction_wow_count=Count("reactions", filter=Q(reactions__kind="wow")),
            reaction_sad_count=Count("reactions", filter=Q(reactions__kind="sad")),
            reaction_fire_count=Count("reactions", filter=Q(reactions__kind="fire")),
        ),
        id=post_id,
    )
    if post.visibility == Post.VISIBILITY_PRIVATE and request.user != post.author:
        return redirect("home")
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
            return redirect("home")
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
            if _is_ajax(request):
                created_at = timezone.localtime(comment.created_at)
                return JsonResponse(
                    {
                        "ok": True,
                        "comments_count": post.comments.count(),
                        "comment": {
                            "id": comment.id,
                            "author": comment.author.username,
                            "author_url": reverse(
                                "profile", kwargs={"username": comment.author.username}
                            ),
                            "body": comment.body,
                            "created_at": created_at.strftime("%b %d, %Y %H:%M"),
                            "can_edit": True,
                            "can_delete": True,
                            "delete_url": reverse(
                                "comment_delete", kwargs={"comment_id": comment.id}
                            ),
                            "edit_url": reverse(
                                "comment_update", kwargs={"comment_id": comment.id}
                            ),
                        },
                    }
                )
        elif _is_ajax(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    if _is_ajax(request):
        return JsonResponse({"ok": False}, status=405)
    return redirect("post_detail", post_id=post.id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post = comment.post
    if request.method == "POST":
        comment.delete()
        if _is_ajax(request):
            return JsonResponse(
                {"ok": True, "comments_count": post.comments.count()}
            )
    if _is_ajax(request):
        return JsonResponse({"ok": False}, status=405)
    return redirect("post_detail", post_id=post.id)


@login_required
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save(update_fields=["body"])
            if _is_ajax(request):
                created_at = timezone.localtime(comment.created_at)
                return JsonResponse(
                    {
                        "ok": True,
                        "comment": {
                            "id": comment.id,
                            "body": comment.body,
                            "created_at": created_at.strftime("%b %d, %Y %H:%M"),
                        },
                    }
                )
        elif _is_ajax(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    if _is_ajax(request):
        return JsonResponse({"ok": False}, status=405)
    return redirect("post_detail", post_id=comment.post_id)


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    if _is_ajax(request):
        return JsonResponse({"ok": True, **_post_reaction_payload(post)})
    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def set_visibility(request, post_id, visibility):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    allowed = {choice[0] for choice in Post.VISIBILITY_CHOICES}
    if visibility in allowed:
        post.visibility = visibility
        post.save(update_fields=["visibility", "updated_at"])
    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def add_reaction(request, post_id, kind):
    post = get_object_or_404(Post, id=post_id)
    allowed = {choice[0] for choice in Reaction.REACTION_CHOICES}
    if kind not in allowed:
        return redirect(request.META.get("HTTP_REFERER", "home"))

    reaction, created = Reaction.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={"kind": kind},
    )
    if not created:
        if reaction.kind == kind:
            reaction.delete()
        else:
            reaction.kind = kind
            reaction.save(update_fields=["kind"])
    if _is_ajax(request):
        return JsonResponse({"ok": True, **_post_reaction_payload(post)})
    return redirect(request.META.get("HTTP_REFERER", "home"))

# Create your views here.
