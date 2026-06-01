from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            if self.instance and self.instance.pk:
                self.fields["visibility"].initial = self.instance.visibility
            else:
                self.fields["visibility"].initial = Post.VISIBILITY_PUBLIC

    class Meta:
        model = Post
        fields = ["content", "image", "visibility"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
            "visibility": forms.HiddenInput(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 1, "placeholder": "Write a comment...", "class": "comment-input"}),
        }
