from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image", "visibility"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
            "visibility": forms.Select(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 1, "placeholder": "Write a comment...", "class": "comment-input"}),
        }
