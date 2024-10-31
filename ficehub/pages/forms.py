from django import forms
from .models import Comment, Post, Hashtag

class PostForm(forms.ModelForm):
    hashtags = forms.ModelMultipleChoiceField(
        queryset=Hashtag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'hashtags', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

