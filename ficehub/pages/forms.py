from django import forms
from .models import Category, Comment, Post, Hashtag
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Only the essential fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
        return user

class PostSearchForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        label="Category"
    )
    hashtags = forms.ModelMultipleChoiceField(
        queryset=Hashtag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Hashtags"
    )
    search_text = forms.CharField(
        max_length=100,
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={'placeholder': 'Search by post name, text, or hashtag'})
    )

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

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Fields for the additional profile data
        fields = ['fullname', 'birthdate', 'group', 'telegram', 'image']